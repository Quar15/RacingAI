using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TopDownCarInput : MonoBehaviour
{
    private TopDownCarController _topDownCarController;

    private void Awake() 
    {
        _topDownCarController = GetComponent<TopDownCarController>();
    }

    private void Update() 
    {
        Vector2 inputVector = Vector2.zero;

        inputVector.x = Input.GetAxis("Vertical");
        inputVector.y = Input.GetAxis("Horizontal");

        _topDownCarController.SetInputVector(inputVector);
    }
}
