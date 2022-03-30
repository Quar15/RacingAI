using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ScoreManager : MonoBehaviour
{
    private float _points = 0.0f;

    public event Action<float> OnUpdatePoints;

    private float _speed;
    private Rigidbody2D _rb;

    private void Awake()
    {
        _rb = transform.GetComponent<Rigidbody2D>();
        ResetPoints();
        InvokeRepeating("ControlSpeed", 10f, .3f);
    }

    public void ResetPoints()
    {
        _points = 0;
    }

    public void AddPoints(float pointsToAdd)
    {
        // Debug.Log($"Points: {_points} ({pointsToAdd})");
        _points += pointsToAdd;
        OnUpdatePoints?.Invoke(pointsToAdd);
    }

    public float Points
    {
        get { return _points; }
    }

    private void ControlSpeed()
    {
        _speed = _rb.velocity.magnitude;

        if(_speed <= 0.1)
        {
            AddPoints(-1.0f);
        }
        else
        {
            float pointsToAdd = Mathf.Clamp(_speed*0.25f, 0f, 5f);
            AddPoints(pointsToAdd);
        }
    }

    private void OnCollisionEnter2D(Collision2D other) 
    {
        _speed = _rb.velocity.magnitude;
        if(other.collider.CompareTag("Wall"))
        {
            AddPoints(-.5f * + _speed);
        }
    }

    private void OnCollisionStay2D(Collision2D other) 
    {
        _speed = _rb.velocity.magnitude;
        if(other.collider.CompareTag("Wall"))
        {
            AddPoints(-.1f * _speed);
        }
    }
}
