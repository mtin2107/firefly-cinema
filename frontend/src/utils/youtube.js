// Shared by trailer playback and mock validation. Only these YouTube forms
// are accepted; unrelated hosts, credentials and ports are rejected.
export function youtubeId(value) {
  try {
    const authority = /^https?:\/\/([^/?#]+)/i.exec(value)?.[1]?.toLowerCase();
    if (!["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"].includes(authority)) return null;
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password || url.port) return null;
    let id;
    if (url.host === "youtu.be") id = url.pathname.slice(1);
    else if (["youtube.com", "www.youtube.com", "m.youtube.com"].includes(url.host)) {
      if (url.pathname === "/watch") id = url.searchParams.get("v");
      else id = url.pathname.match(/^\/(?:shorts|embed)\/([A-Za-z0-9_-]{11})$/)?.[1];
    }
    return /^[A-Za-z0-9_-]{11}$/.test(id ?? "") ? id : null;
  } catch { return null; }
}
