using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class PythonManager : MonoBehaviour
{
    [SerializeField] private string _pathToExe;
    [SerializeField] private bool _presentationMode;
    public System.Diagnostics.Process _process;

    public void StartPythonExec()
    {
        string fullDataPath = Application.dataPath;

        if(!Application.isEditor)
        {
            _pathToExe = System.IO.Path.Combine(
                fullDataPath,
                "pyserve.exe"
            );
        }

        // By default combine will ignore empty strings
        string savePath = System.IO.Path.Combine(
            fullDataPath,
            "saves",
            PlayerPrefs.GetString("loadPath")
        );

        savePath = savePath.Replace(@"\", "/");
        savePath = '\"' + savePath + '\"';

        // Default args
        string pythonArgs = (" -s " + savePath);

        // If load exists
        if (PlayerPrefs.HasKey("loadPath"))
        {
            // Save path ./saves/[loadPath]
            // Check if path exists
            if (System.IO.Directory.Exists(savePath))
            {
                // Find latest file
                string latestFile = "";
                int latestGen = -1;
                // Save filename structure gen<number>.ntp
                foreach (string fileEntry in System.IO.Directory.GetFiles(savePath, "*.ntp"))
                {
                    // get only the number part
                    int currGen = Int32.Parse(System.IO.Path.GetFileNameWithoutExtension(fileEntry).Substring(3));
                    if (currGen > latestGen)
                    {
                        latestFile = fileEntry;
                        latestGen = currGen;
                    }
                }
                if (latestGen > -1)
                {
                    latestFile = latestFile.Replace(@"\", "/");
                    latestFile = '"' + latestFile + '"';
                    pythonArgs += (" -l " + latestFile);
                }

            }
        }

        if(_presentationMode)
        {
            pythonArgs += (" -m presentation");
        }

        Debug.Log(pythonArgs);

        _process = new System.Diagnostics.Process();

        _process.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Normal;
        _process.StartInfo.FileName = _pathToExe;
        _process.StartInfo.Arguments = pythonArgs;

        _process.Start();
    }

    public void AwaitShutdown()
    {
        if(_process.HasExited)
            return;
        
        Debug.Log(_process.ProcessName);

        _process.WaitForExit();
        
        Debug.Log("@INFO: Python process killed");
    }

    private void OnApplicationQuit()
    {
        AwaitShutdown();
    }
}
