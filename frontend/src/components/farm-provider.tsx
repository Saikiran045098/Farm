"use client";
import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react";
import { AnimatePresence, motion, MotionConfig } from "framer-motion";
import { Check, X, AlertCircle } from "lucide-react";
import type { Product, CartItem, User } from "@/lib/types";
import { translations, type Language, type TranslationKey } from "@/i18n/translations";
import { api, json, delay } from "@/lib/client-api";
import { Navigation, Footer } from "@/components/site-chrome";
import { StoreOverlays } from "@/components/store-overlays";
import { usePathname } from "next/navigation";
type FarmContext = {
 language: Language; setLanguage: (language: Language) => void; t: (key: TranslationKey) => string;
 user: User | null; setUser: (user: User | null) => void; ready: boolean; cart: CartItem[]; wishlist: Product[];
 refreshCart: () => Promise<void>; refreshWishlist: () => Promise<void>; addToCart: (product: Product, weight?: string, quantity?: number) => Promise<boolean>;
 updateQuantity: (id: string, quantity: number) => Promise<void>; removeItem: (id: string) => Promise<void>; toggleWishlist: (product: Product) => Promise<void>;
 selectedProduct: Product | null; setSelectedProduct: (p: Product | null) => void; viewProduct: (p: Product | string) => Promise<void>; productLoading: boolean;
 cartOpen: boolean; setCartOpen: (open: boolean) => void; authOpen: boolean; setAuthOpen: (open: boolean) => void; searchOpen: boolean; setSearchOpen: (open: boolean) => void;
 subscriptionOpen: boolean; setSubscriptionOpen: (open: boolean) => void; notify: (text: string, error?: boolean) => void; logout: () => Promise<void>;
};
const Context = createContext<FarmContext | null>(null);
export function useFarm() { const value = useContext(Context); if (!value) throw new Error("FarmProvider is required"); return value; }
export function FarmProvider({ children }: { children: ReactNode }) {
 const [language, setLanguageState] = useState<Language>("en"); const [user, setUser] = useState<User | null>(null); const [ready, setReady] = useState(false);
 const [cart, setCart] = useState<CartItem[]>([]); const [wishlist, setWishlist] = useState<Product[]>([]);
 const [selectedProduct, setSelectedProduct] = useState<Product | null>(null); const [productLoading, setProductLoading] = useState(false);
 const [cartOpen, setCartOpen] = useState(false); const [authOpen, setAuthOpen] = useState(false); const [searchOpen, setSearchOpen] = useState(false); const [subscriptionOpen, setSubscriptionOpen] = useState(false);
 const [toast, setToast] = useState<{ text: string; error: boolean; id: number } | null>(null); const pathname = usePathname();
 const notify = useCallback((text: string, error = false) => setToast({ text, error, id: Date.now() }), []);
 const refreshCart = useCallback(async () => { const data = await api<{ items: CartItem[] }>("cart"); setCart(data.items); }, []);
 const refreshWishlist = useCallback(async () => { const data = await api<{ products: Product[] }>("wishlist"); setWishlist(data.products); }, []);
 useEffect(() => {
  const lang = localStorage.getItem("fb-language"); if (lang === "te") { setLanguageState("te"); document.documentElement.lang = "te"; }
  async function init() { try { const auth = await api<{ user: User | null }>("auth/me"); setUser(auth.user); await refreshCart(); await refreshWishlist(); } catch { notify("Our market is waking up. Please refresh in a moment.", true); } finally { setReady(true); } }
  void init();
 }, [refreshCart, refreshWishlist, notify]);
 useEffect(() => { if (!toast) return; const timeout = setTimeout(() => setToast(null), 4200); return () => clearTimeout(timeout); }, [toast]);
 useEffect(() => { if (cartOpen) void refreshCart().catch(error => notify((error as Error).message, true)); }, [cartOpen, refreshCart, notify]);
 function setLanguage(value: Language) { setLanguageState(value); localStorage.setItem("fb-language", value); document.documentElement.lang = value; }
 async function addToCart(product: Product, weight = product.weight, quantity = 1) {
  try { await Promise.all([api("cart", { method: "POST", body: json({ productId: product.id, weight, quantity }) }), delay(350)]); await refreshCart(); notify(language === "te" ? "🧺 మీ Farm బుట్టలో చేర్చాం!" : "Added to your Farm Basket!"); return true; }
  catch (e) { notify((e as Error).message, true); return false; }
 }
 async function updateQuantity(id: string, quantity: number) {
  if (quantity < 1) return; const previous = cart; setCart(items => items.map(item => item.id === id ? { ...item, quantity } : item));
  try { await api(`cart/${id}`, { method: "PUT", body: json({ quantity }) }); await refreshCart(); } catch (e) { setCart(previous); notify((e as Error).message, true); }
 }
 async function removeItem(id: string) {
  const previous = cart; setCart(items => items.filter(item => item.id !== id));
  try { await api(`cart/${id}`, { method: "DELETE" }); notify("Removed from your basket"); } catch (e) { setCart(previous); notify((e as Error).message, true); }
 }
 async function toggleWishlist(product: Product) {
  const previous = wishlist; const exists = wishlist.some(p => p.id === product.id);
  setWishlist(items => exists ? items.filter(p => p.id !== product.id) : [...items, product]);
  try { await api(exists ? `wishlist/${product.id}` : "wishlist", { method: exists ? "DELETE" : "POST", ...(!exists ? { body: json({ productId: product.id }) } : {}) }); notify(exists ? "Removed from your favourites" : "Saved with a little love ♡"); } catch (e) { setWishlist(previous); notify((e as Error).message, true); }
 }
 async function viewProduct(p: Product | string) {
  setSearchOpen(false); setProductLoading(true);
  try { const [data] = await Promise.all([api<{ product: Product }>(`products/${typeof p === "string" ? p : p.slug}`), delay(650)]); setSelectedProduct(data.product); } catch (e) { notify((e as Error).message, true); } finally { setProductLoading(false); }
 }
 async function logout() { try { await api("auth/logout", { method: "POST" }); setUser(null); await refreshCart(); await refreshWishlist(); notify("Signed out. See you in the village soon!"); } catch (e) { notify((e as Error).message, true); } }
 const value: FarmContext = { language, setLanguage, t: key => translations[language][key], user, setUser, ready, cart, wishlist, refreshCart, refreshWishlist, addToCart, updateQuantity, removeItem, toggleWishlist, selectedProduct, setSelectedProduct, viewProduct, productLoading, cartOpen, setCartOpen, authOpen, setAuthOpen, searchOpen, setSearchOpen, subscriptionOpen, setSubscriptionOpen, notify, logout };
 const isAdmin = pathname.startsWith("/admin");
 return <Context.Provider value={value}><MotionConfig reducedMotion="user">{!isAdmin && <Navigation />}{children}{!isAdmin && <Footer />}<StoreOverlays /><AnimatePresence>{toast && <motion.div key={toast.id} className={`toast ${toast.error ? "toast-error" : ""}`} role="status" initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }}>{toast.error ? <AlertCircle size={20} /> : <span className="toast-check"><Check size={15} /></span>}<span>{toast.text}</span><button onClick={() => setToast(null)} aria-label="Dismiss notification"><X size={16} /></button></motion.div>}</AnimatePresence></MotionConfig></Context.Provider>;
}
