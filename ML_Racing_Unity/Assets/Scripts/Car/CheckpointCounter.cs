using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CheckpointCounter : MonoBehaviour
{
    private int _checkpointCount;
    public int CheckpointCount { get {return _checkpointCount;} }

    [SerializeField] private CheckpointsManager _checkpointManager;
    private ScoreManager _scoreManager;
    
    void Awake()
    {
        _scoreManager = GetComponent<ScoreManager>();
    }

    private void OnTriggerEnter2D(Collider2D other) 
    {
        if(other.gameObject.CompareTag("CheckPoint"))
        {            
            int nextCheckpointId = _checkpointCount % _checkpointManager.AllCheckpointsCount;
            float speed = transform.GetComponent<Rigidbody2D>().velocity.magnitude;

            if(nextCheckpointId == other.GetComponent<Checkpoint>().ID)
            {
                // Correct Checkpoint
                _scoreManager.AddPoints(1f * speed);
                _checkpointCount++;
            }
            else
            {
                // Wrong Checkpoint
                _scoreManager.AddPoints(-1f * speed);
            }
        }
    }

    public Transform GetCheckpointTransform()
    {
        return _checkpointManager.GetCheckpointTransform(_checkpointCount % _checkpointManager.AllCheckpointsCount);
    }

    public void ResetCheckpoints()
    {
        _checkpointCount = 0;
    }
}
