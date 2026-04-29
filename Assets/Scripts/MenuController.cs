using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuController : MonoBehaviour
{
    public void StartGame()
    {
        SceneManager.LoadScene("SampleScene"); // Substitua pelo nome da sua cena de jogo
    }

    //public void QuitGame()
    //{
    //    Debug.Log("Jogo Encerrado!");
    //    Application.Quit(); // Encerra o jogo (funciona no build final, n�o no editor)
    //}
}
