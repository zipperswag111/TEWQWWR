# LiveVault free GitHub recording worker

This repository runs a **user-started GitHub Actions job** to capture an accessible, public TikTok LIVE stream without leaving a browser tab open.

## Start recording

1. Open the [LiveVault website](https://livevault-tiktok-recorder.vercel.app/).
2. In the Free GitHub Recorder section, provide your TikTok creator username and a fine-grained GitHub token with **Actions: Read and write** access limited to this repository. The token is sent through the LiveVault Vercel function but is **not saved by LiveVault**.
3. Click **Start background recording**. Recording begins only once GitHub Actions starts and resolves a current public LIVE stream.
4. Close LiveVault. The GitHub Actions job continues independently, up to its time or recording size limits.
5. Download the video via the GitHub Actions run's **Artifacts** section. Download promptly; artifacts are retained for **one day**.

The worker starts from the moment it connects; it cannot recover a creator's past LIVE footage. A public stream might be inaccessible to GitHub-hosted IPs, may go offline, and may contain no video. Uploading a file only occurs when the job finishes.

## Free-tier safeguards

- Maximum duration: **5 hours 20 minutes**, to leave time to upload before GitHub's 6-hour job cutoff.
- Recording budget: approximately **400 MiB** of video per run; high-bitrate streams will end earlier.
- Only one running job at a time.
- Artifact retention: **1 day**.
- The repository is currently **public**. GitHub Actions run logs and artifact links may be visible to other users. Do not record private or nonpublic content.
- Public-repository standard GitHub-hosted runner compute is free, but GitHub artifact storage quotas and billing may still apply. Keep billing limits at zero and check [GitHub Actions usage](https://docs.github.com/en/actions/concepts/billing-and-usage).
- No paid hosting is provisioned by this project.

## Security

Use a fine-grained token restricted to **this repository only**, granting **Actions: Read and write** and required metadata read permission. Do not add personal tokens to GitHub commits, actions secrets intended for the website, screenshots, or public pages. The LiveVault site relays the token over HTTPS, does not log it deliberately, and never saves it in Vercel environment variables or GitHub source.

Record only broadcasts you have the right to archive. Independent project; not affiliated with TikTok.
