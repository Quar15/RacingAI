using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WheelTrailRendererHandler : MonoBehaviour
{
    private TopDownCarController _topDownCarController;
    private TrailRenderer _trailRenderer;

    private void Awake() 
    {
        _topDownCarController = GetComponentInParent<TopDownCarController>();

        _trailRenderer = GetComponent<TrailRenderer>();
        _trailRenderer.emitting = false;
    }

    private void Update()
    {
        if(_topDownCarController.IsTireScreeching(out float lateralVelocity, out bool isBraking))
            _trailRenderer.emitting = true;
        else
            _trailRenderer.emitting = false;
    }
}
