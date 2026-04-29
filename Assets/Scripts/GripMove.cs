using System.Collections;
using UnityEngine;

public class GripMove : MonoBehaviour
{
    private float speed;
    private float originalSpeed;
    private float duration = 1.0f;

    public void Initialize(float moveSpeed)
    {
        speed = moveSpeed;
        originalSpeed = moveSpeed;
    }

    /// <summary>
    /// Empurra o objeto para trás por um tempo limitado.
    /// </summary>
    public void PushBack(float force, float duration)
    {
        StopAllCoroutines();   // impede conflitos se ocorrer pushback múltiplas vezes
        StartCoroutine(PushBackRoutine(force, duration));
    }

    private IEnumerator PushBackRoutine(float force, float duration)
    {
        speed = -force;               // velocidade reversa
        yield return new WaitForSeconds(duration);

        speed = originalSpeed;       // volta ao normal
    }

    private void Update()
    {
        // Move o objeto
        transform.Translate(Vector3.back * speed * Time.deltaTime);

        // Destruir ao sair da tela
        if (transform.position.z < -720f)
        {
            Destroy(gameObject);
        }
    }
}
