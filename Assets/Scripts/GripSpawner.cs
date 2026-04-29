using System.Collections;
using UnityEngine;

public class GripSpawner : MonoBehaviour
{
    [Header("Spawn settings")]
    public GameObject[] objects;
    public Transform objectParent;
    public float spawnIntervalMin = 3f;
    public float spawnIntervalMax = 5f;
    public float objectSpeed = 8f;

    private bool canSpawn = true;

    private void Start()
    {
        StartCoroutine(SpawnObjectLoop());
    }

    private IEnumerator SpawnObjectLoop()
    {
        while (true)
        {
            if (canSpawn)
            {
                float spawnDelay = Random.Range(spawnIntervalMin, spawnIntervalMax);
                SpawnCenteredObject();
                yield return new WaitForSeconds(spawnDelay);
            }
            else
            {
                // espera 1 frame e continua verificando
                yield return null;
            }
        }
    }

    public void StopSpawn()
    {
        canSpawn = false;
    }

    public void StartSpawn()
    {
        canSpawn = true;
    }

    private void SpawnCenteredObject()
    {
        if (objects.Length == 0) return;

        int randomIndex = Random.Range(0, objects.Length);
        GameObject selectedObject = objects[randomIndex];

        GameObject obj = Instantiate(selectedObject, transform.position, Quaternion.identity, objectParent);

        // adiciona ou pega o GripMove
        GripMove gripMove = obj.GetComponent<GripMove>();
        if (gripMove == null)
            gripMove = obj.AddComponent<GripMove>();

        gripMove.Initialize(objectSpeed);
    }
}
