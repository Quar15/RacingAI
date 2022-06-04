using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class PauseMenu : MonoBehaviour
{
    [SerializeField] private TCPConnection _tcpConnection;
    [SerializeField] private PythonManager _pythonManager;
    private RectTransform rTransform;

    private void Awake() 
    {
        rTransform = GetComponent<RectTransform>();
    }

    private void Update()
    {
        if(Input.GetKeyDown(KeyCode.Escape))
            SwitchPanelVisibility();
    }

    public void SwitchPanelVisibility()
    {
        if(rTransform.localPosition.y != 0)
        {
            rTransform.localPosition = new Vector3(0f, 0f, 0f);
        }
        else
        {
            rTransform.localPosition = new Vector3(0f, -3000f, 0f);
        }
        
    }

    public void ExitToMenu()
    {
        _tcpConnection.SendShutdown();
        _pythonManager.AwaitShutdown();
        SceneManager.LoadScene("Menu");
    }
}
