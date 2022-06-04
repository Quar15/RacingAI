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
        _bestScore = -1000;
        _bestCheckpoints = -1;
        UpdateText(0, 0, -100);
    }

    public void UpdateText(int gen, int checkpoints, float score)
    {
        if(!scoreText)
            return;

        if(checkpoints > _bestCheckpoints)
            _bestCheckpoints = checkpoints;

        if(score > _bestScore)
            _bestScore = score;

        scoreText.text = $"Gen: {gen}\nBest Score: {_bestScore}\nBest Checkpoints: {_bestCheckpoints}";
    }
}
