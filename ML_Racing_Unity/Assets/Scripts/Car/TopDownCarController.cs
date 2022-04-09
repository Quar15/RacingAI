using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TopDownCarController : MonoBehaviour
{
    [Header("Car Settings")]
    [SerializeField] private float _driftFactor = 0.95f;
    [SerializeField] private float _accelerationFactor = 30.0f;
    [SerializeField] private float _turnFactor = 3.5f;
    [SerializeField] private float _maxSpeed = 20.0f;
    [SerializeField] private float _maxReverseSpeed = 10.0f;

    private float _accelerationInput = 0;
    private float _steeringInput = 0;

    private float _rotationAngle = 0;

    private float _velocityVsUp = 0;

    private Rigidbody2D _carRB;

    private void Awake() 
    {
        _carRB = GetComponent<Rigidbody2D>();
    }

    private void FixedUpdate()
    {
        ApplyEngineForce();

        KillOrthogonalVelocity();

        ApplySteering();
    }

    private void ApplyEngineForce()
    {
        _velocityVsUp = Vector2.Dot(transform.up, _carRB.velocity);

        if(_velocityVsUp > _maxSpeed && _accelerationInput > 0)
            return;

        if(_velocityVsUp < -_maxReverseSpeed && _accelerationInput < 0)
            return;

        if(_carRB.velocity.sqrMagnitude > _maxSpeed * _maxSpeed && _accelerationInput > 0)
            return;

        if(_accelerationInput == 0)
            _carRB.drag = Mathf.Lerp(_carRB.drag, 3.0f, Time.fixedDeltaTime * 3);
        else
            _carRB.drag = 0;

        Vector2 engineForceVector = transform.up * _accelerationInput * _accelerationFactor;

        _carRB.AddForce(engineForceVector, ForceMode2D.Force);
    }

    private void ApplySteering()
    {
        float minSpeedBeforeAllowTurningFactor = (_carRB.velocity.magnitude / 8);
        minSpeedBeforeAllowTurningFactor = Mathf.Clamp01(minSpeedBeforeAllowTurningFactor);

        _rotationAngle -= _steeringInput * _turnFactor * minSpeedBeforeAllowTurningFactor;

        _carRB.MoveRotation(_rotationAngle);
    }

    private void KillOrthogonalVelocity()
    {
        Vector2 forwardVelocity = transform.up * Vector2.Dot(_carRB.velocity, transform.up);
        Vector2 rightVelocity = transform.right * Vector2.Dot(_carRB.velocity, transform.right);

        _carRB.velocity = forwardVelocity + rightVelocity * _driftFactor;
    }

    private float GetLateralVelocity()
    {
        return Vector2.Dot(transform.right, _carRB.velocity);
    }

    public float GetVelocityMagnitude()
    {
        return _carRB.velocity.magnitude;
    } 

    public bool IsTireScreeching(out float lateralVelocity, out bool isBraking)
    {
        lateralVelocity = GetLateralVelocity();

        isBraking = false;
        if(_accelerationInput < 0 && _velocityVsUp > 0)
        {
            isBraking = true;
            return true;
        }

        if(Mathf.Abs(GetLateralVelocity()) > 4.0f)
            return true;

        return false;
    }

    public void SetInputVector(Vector2 inputVector)
    {
        _accelerationInput = inputVector.x;
        _steeringInput = inputVector.y;
    }

    public void ResetEngine(float startingPointRotation = 0.0f)
    {
        SetInputVector(Vector2.zero);
        _carRB.velocity = Vector2.zero;
        _carRB.angularVelocity = 0f;
        _rotationAngle = startingPointRotation;
        _velocityVsUp = 0;
    }
}
