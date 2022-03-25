using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CheckpointsManager : MonoBehaviour
{
    [SerializeField] private Transform[] _checkpoints;

    public int AllCheckpointsCount { get { return _checkpoints.Length; } }

    public Transform GetCheckpointTransform(int checkpointIndex)
    {
        return _checkpoints[checkpointIndex];
    }
}
