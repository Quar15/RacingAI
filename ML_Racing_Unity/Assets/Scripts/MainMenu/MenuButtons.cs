using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuButtons : MonoBehaviour
{
    [SerializeField] private GameObject _learnPanel;
    [SerializeField] private GameObject _creditsPanel;

    private void LoadLevel(string levelName)
    {
        SceneManager.LoadScene(levelName);
    }

    public void Presentation()
    {
        LoadLevel("Main_Presentation");
    }

    public void OpenLearnPanel()
    {
        _learnPanel.SetActive(true);
    }

    public void CloseLearnPanel()
    {
        _learnPanel.SetActive(false);
    }

    public void OpenLearningLevel(int levelID)
    {
        switch (levelID)
        {
            case 0:
                LoadLevel("Main_Clockwise");
                break;
            case 1:
                LoadLevel("Main_Counterclockwise");
                break;
            case 2:
                LoadLevel("Main_Track");
                break;
            case 3:
                LoadLevel("Main");
                break;
            default:
                Debug.LogError("Wrong levelID!");
                break;
        }
    }

    public void OpenCredits()
    {
        _creditsPanel.SetActive(true);
    }

    public void CloseCredits()
    {
        _creditsPanel.SetActive(false);
    }

    public void Quit()
    {
        Application.Quit();
    }
}
