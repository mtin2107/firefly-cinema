import { useEffect } from "react";
export function usePageTitle(title) {
  useEffect(() => { document.title = title ? `${title} – Firefly Cinema` : "Firefly Cinema"; }, [title]);
}
export function returnTo(from) {
  return from?.pathname?.startsWith("/") && !from.pathname.startsWith("//")
    && !["/dang-nhap", "/dang-ky"].includes(from.pathname)
    ? `${from.pathname}${from.search ?? ""}${from.hash ?? ""}` : "/";
}
