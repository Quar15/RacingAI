using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.SceneManagement;

public class MenuButtons : MonoBehaviour
{
    [SerializeField] private GameObject _learnPanel;
    [SerializeField] private GameObject _learnOptionsPanel;
    [SerializeField] private TMP_InputField _learnOptionsMaxStepsInput;
    [SerializeField] private TMP_InputField _learnOptionsRelativePathInput;
    [SerializeField] private TextMeshProUGUI _activePathText;
    [SerializeField] private GameObject _optionsPanel;
    [SerializeField] private GameObject _creditsPanel;
    
    private void Start() 
    {
        _activePathText.text = Application.dataPath + "/saves/";
        if(PlayerPrefs.HasKey("loadPath"))
            _learnOptionsRelativePathInput.text = PlayerPrefs.GetString("loadPath");
        
        if(PlayerPrefs.HasKey("maxSteps"))
            _learnOptionsMaxStepsInput.text = PlayerPrefs.GetInt("maxSteps").ToString();
    }


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

    public void SwitchLearningOptionsPanel()
    {
        _learnOptionsPanel.SetActive(!_learnOptionsPanel.activeSelf);
    }

    public void SetMaxNumberOfSteps()
    {
        int maxStepsInputVal = System.Int32.Parse(_learnOptionsMaxStepsInput.text);
        if(maxStepsInputVal > 0)
            PlayerPrefs.SetInt("maxSteps", maxStepsInputVal);
    }

    public void SetLoadPath()
    {
        string pathText = _learnOptionsRelativePathInput.text;
        if(pathText.Length > 0 && pathText.Substring(pathText.Length-1, 1) != "/")
            pathText += "/";
        PlayerPrefs.SetString("loadPath", pathText);
    }

    public void OpenCredits()
    {
        _creditsPanel.SetActive(true);
    }

    public void CloseCredits()
    {
        _creditsPanel.SetActive(false);
    }

    public void OpenOptions()
    {
        _optionsPanel.SetActive(true);
    }

    public void CloseOptions()
    {
        _optionsPanel.SetActive(false);
    }

    public void Quit()
    {
        Application.Quit();
    }
}
