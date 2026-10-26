import { createContext, useContext, useEffect, useState } from "react";
import { api, tokenStore } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  // Mở trang: nếu đã có token thì hỏi backend xem token còn hợp lệ không
  useEffect(() => {
    if (!tokenStore.get()) { setChecking(false); return; }
    api.auth.me()
      .then(setUser)
      .catch(() => tokenStore.set(null))
      .finally(() => setChecking(false));
  }, []);

  const handleAuth = ({ access_token, user }) => {
    tokenStore.set(access_token);
    setUser(user);
    return user;
  };

  const value = {
    user,
    checking,
    changeEmail: async (payload) => { const updated = await api.auth.changeEmail(payload); setUser(updated); return updated; },
    putAvatar: async (payload) => { const updated = await api.auth.putAvatar(payload); setUser(updated); return updated; },
    deleteAvatar: async () => { const updated = await api.auth.deleteAvatar(); setUser(updated); return updated; },
    login: async (email, password) => handleAuth(await api.auth.login({ email, password })),
    register: async (full_name, email, password) => handleAuth(await api.auth.register({ full_name, email, password })),
    updateProfile: async (profile) => {
      const updated = await api.auth.updateMe(typeof profile === "string" ? { full_name: profile } : profile);
      setUser(updated);
      return updated;
    },
    changePassword: (current_password, new_password) => api.auth.changePassword({ current_password, new_password }),
    logout: () => { tokenStore.set(null); setUser(null); },
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
