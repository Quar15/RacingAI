using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class CarStatsUI : MonoBehaviour
{
    public TextMeshProUGUI scoreText;

    private float _bestScore;
    private int _bestCheckpoints;

    // Start is called before the first frame update
    void Start()
    {
        UpdateText(0, 0, 0, 0);
    }

    public void UpdateText(int gen, float time, int checkpoints, float score)
    {
        if(!scoreText)
            return;

        if(checkpoints > _bestCheckpoints)
            _bestCheckpoints = checkpoints;

        if(score > _bestScore)
            _bestScore = score;

        scoreText.text = $"Gen: {gen}\nTime: {time}\nCheckpoints: {checkpoints}\nScore: {score}\nBestScore: {_bestScore}\nBest Checkpoints: {_bestCheckpoints}";
    }
}
