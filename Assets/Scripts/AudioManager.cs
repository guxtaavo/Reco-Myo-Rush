using UnityEngine;

public class AudioManager : MonoBehaviour
{
    [Header("Audio Sources")]
    [SerializeField] AudioSource musicSource;
    [SerializeField] AudioSource sfxSource;
    // Start is called before the first frame update

    [Header("Audio Clips")]
    public AudioClip backgroundMusic;
    public AudioClip menuMusic;
    public AudioClip deathSound;
    public AudioClip buttonSound;

    private void Start() {
        musicSource.clip = backgroundMusic;
        musicSource.loop = true;
        musicSource.Play();
    }

    public void PlaySfx(AudioClip clip)
    {
        sfxSource.PlayOneShot(clip);
        sfxSource.Play();
    }
}
