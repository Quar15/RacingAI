using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class PythonManager : MonoBehaviour
{
    [SerializeField] private string _pathToExe;
    
    public void StartPythonExec()
    {
        string savePath = Application.dataPath + "/saves/";
        // Default args
        string pythonArgs = ("-s " + savePath);
        // If load exists
        if(PlayerPrefs.HasKey("loadPath"))
        {
            // Save path ./saves/[loadPath]
            savePath += PlayerPrefs.GetString("loadPath");
            pythonArgs = ("-s " + savePath);
            // Check if path exists
            if(System.IO.Directory.Exists(savePath))
            {
                // Find latest file
                string[] fileEntries = System.IO.Directory.GetFiles(savePath);
                if(fileEntries.Length - System.IO.Directory.GetDirectories(savePath).Length > 0)
                {
                    string latestFile = savePath + "gen0.ntp";

                    foreach(string fileName in fileEntries)
                    {
                        if(fileName.Substring(fileName.Length-4, 4) == "meta" || fileName.Substring(fileName.Length-3, 3) != "ntp")
                            continue;
                        
                        if(Int32.Parse(latestFile.Substring(savePath.Length + 3, latestFile.Length - savePath.Length - 7)) < Int32.Parse(fileName.Substring(savePath.Length + 3, fileName.Length - savePath.Length - 7)))
                            latestFile = fileName;
                    }
                    // Add latest file path to args
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
