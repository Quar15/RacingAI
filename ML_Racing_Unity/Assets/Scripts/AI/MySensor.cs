using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MySensor : MonoBehaviour
{
    [SerializeField] private LayerMask _blockingMask;
    [SerializeField] private float _maxDistance = 50f;

    public bool ShouldDrawGizmos = false;
    public bool ShouldDrawGizmosInGame = false;

    [SerializeField] private Transform[] _inGameDebugCubes;
    [SerializeField] private Transform[] _inGameDebugCircles;

    private Color[] _gizmosColors = {Color.blue, Color.green, Color.red, Color.cyan, Color.black, Color.magenta, Color.yellow, Color.white};

    private RaycastHit2D[] _lastFrameRays;

    private float[] _sensorData = new float[7];

    // Update is called once per frame
    void Update()
    {
        Vector2[] _raycastsDirections = {-transform.right, (transform.up - transform.right*2), (transform.up - transform.right/2), transform.up, (transform.up + transform.right/2), (transform.up + transform.right*2), transform.right};

        RaycastHit2D ray;
        List<RaycastHit2D> currFrameRays = new List<RaycastHit2D>();

        for(int i=0; i < _raycastsDirections.Length; i++)
        {
            ray = Physics2D.Raycast(transform.position, _raycastsDirections[i], _maxDistance, _blockingMask);
            UpdateCube(ray, i, _gizmosColors[i]);
            currFrameRays.Add(ray);
        }

        _lastFrameRays = currFrameRays.ToArray();
        
        for(int i=0; i < _lastFrameRays.Length; i++)
            _sensorData[i] = _lastFrameRays[i].distance;
    }

    private void OnDrawGizmos()
    {
        if(!ShouldDrawGizmos)
            return;

        for(int i=0; i < _lastFrameRays.Length; i++)
        {
            DrawRaycast(_lastFrameRays[i], _gizmosColors[i], _gizmosColors[i]);
        }
    }

    private void DrawRaycast(RaycastHit2D ray, Color rayColor, Color circleColor)
    {
        if(ray.point != null)
        {
            Gizmos.color = rayColor;
            Gizmos.DrawLine(transform.position, ray.point);

            Gizmos.color = circleColor;
            Gizmos.DrawSphere(new Vector3(ray.point.x, ray.point.y), .3f);
        }
    }

    private void UpdateCube(RaycastHit2D ray, int debugCubeIndex, Color debugColor)
    {
        _inGameDebugCubes[debugCubeIndex].position = (new Vector3(ray.point.x, ray.point.y) + new Vector3(transform.position.x, transform.position.y)) / 2;
        _inGameDebugCubes[debugCubeIndex].localScale = (new Vector3(ray.distance - ray.distance*0.2f, .1f, .1f));
        _inGameDebugCubes[debugCubeIndex].GetComponent<SpriteRenderer>().color = debugColor;

        _inGameDebugCircles[debugCubeIndex].position = ray.point;
        _inGameDebugCircles[debugCubeIndex].GetComponent<SpriteRenderer>().color = debugColor;

        if(!ShouldDrawGizmosInGame)
        {
            _inGameDebugCubes[debugCubeIndex].GetComponent<SpriteRenderer>().color = Color.clear;
            _inGameDebugCircles[debugCubeIndex].GetComponent<SpriteRenderer>().color = Color.clear;
        }
    }

    public float[] GetSensorData()
    {
        return _sensorData;
    }
}
