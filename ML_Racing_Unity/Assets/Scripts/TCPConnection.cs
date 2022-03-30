using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Globalization;

using UnityEngine;

public class TCPConnection : MonoBehaviour 
{
    private const int HEADER_SIZE = 16;
    Thread receiveThread;
    TcpClient lClient;
    TcpListener listener;
    [SerializeField] private int _listenPort = 5066;
    [SerializeField] private string _listenIp = "127.0.0.1";

    private string _logging_text;

    public List<MyAgent> agents;

    private void Awake()
    {
        InitTCP();
        InvokeRepeating("SendAgentsData", 10, 0.3f);

        Application.runInBackground = true;
    }

    private void SendAgentsData()
    {
        for(int i=0; i < agents.Count; i++)
            agents[i].SendAgentData();
    }

    private void InitTCP()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        bool new_msg = true;
        int msg_len = -1;
        string full_msg = "";
        try {
            listener = new TcpListener(IPAddress.Parse(_listenIp), _listenPort);
            listener.Start();
            Byte[] bytes = new Byte[16];

            while (true) {
                using(lClient = listener.AcceptTcpClient()) {
                    using (NetworkStream stream = lClient.GetStream()) {
                        int length;
                        while ((length = stream.Read(bytes, 0, bytes.Length)) != 0) {
                            var incommingData = new byte[length];
                            Array.Copy(bytes, 0, incommingData, 0, length);
                            string clientMessage = Encoding.UTF8.GetString(incommingData);

                            if(new_msg)
                            {
                                int.TryParse(clientMessage, out msg_len);
                                new_msg = false;
                            }

                            if(msg_len < 0)
                            {
                                new_msg = true;
                                continue;
                            }

                            full_msg += clientMessage;

                            if(full_msg.Length - HEADER_SIZE == msg_len)
                            {
                                ProcessData(full_msg);
                                new_msg = true;
                                full_msg = "";
                            }

                            _logging_text = clientMessage;
                        }
                    }
                }
            }
        } catch(Exception e) {
            print(e.ToString());
            _logging_text = e.ToString();
        }
    }

    public void SendMessageTCP(string msg)
    {
        msg = "#" + msg + "#";
        while(msg.Length % 16 != 0)
            msg += " ";

        // Create header
        string header = msg.Length.ToString();
        while(header.Length < HEADER_SIZE)
            header += " ";
        
        msg = header + msg;

        // Debug.Log($"MSG: {msg}");

        try
        {
            // Get a stream object for writing.		
            NetworkStream stream = lClient.GetStream(); 			
            if (stream.CanWrite)
            {	
                // Convert string message to byte array.
                byte[] clientMsgAsByteArray = Encoding.UTF8.GetBytes(msg);		
                // Write byte array to socketConnection stream.
                stream.Write(clientMsgAsByteArray, 0, clientMsgAsByteArray.Length);           
                Debug.Log("Client sent his message - should be received by server");
            }
        }
        catch (SocketException socketException)
        {
            Debug.Log("Socket exception: " + socketException); 
        }
    }

    private void ProcessData(string msg)
    {
        string[] data = msg.Split('#')[1].Split(' ');
        
        int gen = (int) float.Parse(data[0], CultureInfo.InvariantCulture);

        if(gen != agents[agents.Count-1].generation)
            return;

        int carId = (int) float.Parse(data[1], CultureInfo.InvariantCulture);

        // float verticalInput = float.Parse(data[2], CultureInfo.InvariantCulture);
        // float horizontalInput = float.Parse(data[3], CultureInfo.InvariantCulture);
        // Debug.Log($"Gen: {gen}, car_id: {carId}, verticalInput: {verticalInput}, horizontalInput: {horizontalInput}");

        float[] input = {float.Parse(data[2], CultureInfo.InvariantCulture), float.Parse(data[3], CultureInfo.InvariantCulture)};
        

        foreach (var agent in agents)
        {
            if(agent.agentId == carId)
            {
                agent.OnActionReceived(input);
                // Debug.Log($"Gen: {gen}, car_id: {carId}, verticalInput: {input[0]}, horizontalInput: {input[1]}");
                break;
            }
        }
    }

    private void ShutdownConnection()
    {
        if(receiveThread != null)
            receiveThread.Abort();

        lClient.Close();
    }

    private void OnDisable() 
    {
        ShutdownConnection();
    }

    private void OnApplicationQuit()
    {
        ShutdownConnection();
    }
}