using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class PythonManager : MonoBehaviour
{
    [SerializeField] private string _pathToExe;

    public void StartPythonExec()
    {
        // By default combine will ignore empty strings
        string savePath = System.IO.Path.Combine(
            System.IO.Path.GetFullPath(Application.dataPath),
            "saves",
            PlayerPrefs.GetString("loadPath")
        );

        // Default args
        string pythonArgs = ("-s " + savePath);

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
                    pythonArgs += (" -l " + latestFile);
                }

            }
        }

        Debug.Log(pythonArgs);

        System.Diagnostics.Process process = new System.Diagnostics.Process();

        process.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Normal;
        process.StartInfo.FileName = _pathToExe;
        process.StartInfo.Arguments = pythonArgs;

        process.Start();
    }
}
