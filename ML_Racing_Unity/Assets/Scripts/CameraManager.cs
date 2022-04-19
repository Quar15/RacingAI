using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraManager : MonoBehaviour
{

    public GameObject[] virtCameraList;
    private int currCamera;

    
    void Start()
    {
        currCamera = 0;
        for(int i=0; i < virtCameraList.Length; i++)
            virtCameraList[i].SetActive(false);

        virtCameraList[0].SetActive(true);
    }

    
    void Update()
    {
        if (Input.GetMouseButtonUp(0)){
            currCamera ++;
            if (currCamera < virtCameraList.Length){
                virtCameraList[currCamera - 1].gameObject.SetActive(false);
                virtCameraList[currCamera].gameObject.SetActive(true);
            }
            else {
                currCamera = 0;
                virtCameraList[currCamera].gameObject.SetActive(true);
            }
        }
    }
}
