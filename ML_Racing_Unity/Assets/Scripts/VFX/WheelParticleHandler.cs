using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WheelParticleHandler : MonoBehaviour
{
    private TopDownCarController _topDownCarController;
    private ParticleSystem _particleSystemSmoke;
    private ParticleSystem.EmissionModule _particleSystemEmissionModule;

    private float _particleEmissionRate = 0;

    private void Awake() 
    {
        _topDownCarController = GetComponentInParent<TopDownCarController>();

        _particleSystemSmoke = GetComponent<ParticleSystem>();
        _particleSystemEmissionModule = _particleSystemSmoke.emission;
        _particleSystemEmissionModule.rateOverTime = 0;
    }

    private void Update() 
    {
        // Reduce particles over time
        _particleEmissionRate = Mathf.Lerp(_particleEmissionRate, 0, Time.deltaTime * 5);
        _particleSystemEmissionModule.rateOverTime = _particleEmissionRate;

        if(_topDownCarController.IsTireScreeching(out float lateralVelocity, out bool isBraking))
        {
            if(isBraking)
                _particleEmissionRate = 30; // Brake smoke emission
            else
                _particleEmissionRate = Mathf.Abs(lateralVelocity) * 2; // Drift smoke emission
        }
    }
}
