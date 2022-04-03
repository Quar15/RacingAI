using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MyAgent : MonoBehaviour
{
    [SerializeField] private int _maxSteps = 1200;
    private int _steps;

    [Header("References")]
    [SerializeField] private TCPConnection _tcpConnectionManager;
    [SerializeField] private Transform _spawnTransform;
    [SerializeField] private CarStatsUI _carStats;
    
    private MySensor _sensor;
    private TopDownCarController _topDownCarController;
    private ScoreManager _scoreManager;
    private CheckpointCounter _checkpointCounter;

    public int agentId;
    public int generation;

    void Awake()
    {
        _topDownCarController = GetComponent<TopDownCarController>();
        _sensor = GetComponent<MySensor>();
        _tcpConnectionManager.agents.Add(this);
        _scoreManager = GetComponent<ScoreManager>();
        _checkpointCounter = GetComponent<CheckpointCounter>();
    }

    private void Start()
    {
        EndEpisode();
    }

    private void Update()
    {
        if(_steps >= _maxSteps)
            EndEpisode();
    }

    private void UpdateCarStats()
    {
        if(_carStats != null)
        {
            _carStats.UpdateText(generation, _checkpointCounter.CheckpointCount, _scoreManager.Points);
        }
    }

    private Transform GetNextCheckpoint()
    {
        return _checkpointCounter.GetCheckpointTransform();
    }

    private string Vector3ToString2D(Vector3 v)
    {
        return v.x.ToString("F4") + " " + v.y.ToString("F4");
    }

    public void SendAgentData()
    {
        string msg = "";

        // Generation
        msg += generation.ToString() + " ";

        // Agent ID
        msg += agentId.ToString() + " ";
        
        // Distance from walls
        float[] sensorData = _sensor.GetSensorData();
        for(int i=0; i < sensorData.Length; i++)
            msg += sensorData[i].ToString("F4") + " ";

        // Car position
        msg += Vector3ToString2D(transform.position) + " ";

        // Car speed
        msg += transform.GetComponent<Rigidbody2D>().velocity.magnitude.ToString("F4") + " ";

        // Checkpoint position and relative rotation to car
        Transform checkpointTransform = GetNextCheckpoint();
        Vector3 checkpointForward = checkpointTransform.transform.forward;
        float dirDot = Vector3.Dot(transform.forward, checkpointForward);

        msg += Vector3ToString2D(checkpointTransform.position) + " ";
        msg += dirDot.ToString("F4") + " ";

        msg += _scoreManager.Points.ToString("F4");

        // Debug.Log(msg);

        _tcpConnectionManager.SendMessageTCP(msg);

        UpdateCarStats();
    }

    public void OnActionReceived(float[] actions)
    {
        float forwardAmount = actions[0];
        float turnAmount = actions[1];

        // Debug.Log($"({forwardAmount}, {turnAmount})");

        _topDownCarController.SetInputVector(new Vector2(forwardAmount, turnAmount));

        _steps++;
    }

    public void EndEpisode()
    {
        _topDownCarController.ResetEngine();

        transform.position = _spawnTransform.position + new Vector3(Random.Range(-1.0f, +1.0f), 0, 0);
        transform.rotation = _spawnTransform.rotation;

        _scoreManager.ResetPoints();
        _checkpointCounter.ResetCheckpoints();

        _steps = 0;
        generation++;

        UpdateCarStats();
    }
}
