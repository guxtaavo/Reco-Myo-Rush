using System.Collections;
using UnityEngine;

public class CheckCollider : MonoBehaviour
{
    public GripSpawner spawner;        // arraste no inspetor
    public float penaltyTime = 2f;     // tempo de bloqueio do spawn
    public float pushBackForce = 20f;  // velocidade negativa quando erra

    private bool blocked = false;      // evita ativar penalidade 2x

    private void OnTriggerEnter(Collider other)
    {
        string tag = other.tag;

        // Agora checando 3 grips
        int planoID = 
            (tag == "Grip1") ? 1 :
            (tag == "Grip2") ? 2 :
            (tag == "Grip3") ? 3 : 0;

        if (planoID == 0) return; // ignora objetos sem tag de grip

        Debug.Log("Plano detectado: " + planoID);

        // Verifica se o plano detectado é o mesmo enviado pelo Python
        if (planoID == GripInput.gripAtual)
        {
            Debug.Log("✔ ACERTOU o Grip " + planoID);
        }
        else
        {
            Debug.Log("❌ ERROU! Grip esperado: " + GripInput.gripAtual);

            if (!blocked)
            {
                StartCoroutine(Penalidade());
            }
        }
    }

    IEnumerator Penalidade()
    {
        blocked = true;

        spawner.StopSpawn();

        // empurra todos que estão no cenário
        foreach (GripMove gm in FindObjectsOfType<GripMove>())
        {
            gm.PushBack(pushBackForce, 0.5f);
        }

        yield return new WaitForSeconds(penaltyTime);

        spawner.StartSpawn();
        blocked = false;
    }
}
