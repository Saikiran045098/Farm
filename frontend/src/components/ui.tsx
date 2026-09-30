"use client";
import { useEffect, useRef, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Sprout, Wheat, Leaf, ArrowRight } from "lucide-react";
import Link from "next/link";
export function Modal({ children, onClose, label, className = "" }: { children: ReactNode; onClose: () => void; label: string; className?: string }) {
 const ref = useRef<HTMLDivElement>(null);
 const closeRef = useRef(onClose);
 useEffect(() => { closeRef.current = onClose; }, [onClose]);
 useEffect(() => {
  const previous = document.activeElement as HTMLElement; const overflow = document.body.style.overflow; document.body.style.overflow = "hidden";
  const panel = ref.current; const input = panel?.querySelector<HTMLInputElement>('input:not([type="checkbox"])'); (input || panel)?.focus();
  const keydown = (e: KeyboardEvent) => { if (e.key === "Escape") closeRef.current(); if (e.key === "Tab" && panel) { const nodes = Array.from(panel.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input:not([disabled]), select, textarea, [tabindex="0"]')); const first = nodes[0], last = nodes[nodes.length - 1]; if (e.shiftKey && (document.activeElement === first || document.activeElement === panel)) { e.preventDefault(); last?.focus(); } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); } } };
  document.addEventListener("keydown", keydown); return () => { document.body.style.overflow = overflow; document.removeEventListener("keydown", keydown); previous?.focus(); };
 }, []);
 return <motion.div className="modal-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={e => { if (e.target === e.currentTarget) onClose(); }}><motion.div ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={label} className={`modal-panel ${className}`} initial={{ y: 28, opacity: 0, scale: .97 }} animate={{ y: 0, opacity: 1, scale: 1 }} exit={{ y: 20, opacity: 0 }}><button className="modal-close icon-button" onClick={onClose} aria-label="Close dialog"><X size={20} /></button>{children}</motion.div></motion.div>;
}
export function FarmLoader({ text = "Freshness is on its way…", small = false }: { text?: string; small?: boolean }) { return <div className={`farm-loader ${small ? "small" : ""}`} role="status"><div className="growing-icons">{[Leaf, Sprout, Wheat].map((Icon, i) => <motion.span key={i} animate={{ y: [0, -7, 0], opacity: [.45, 1, .45] }} transition={{ duration: 1.6, repeat: Infinity, delay: i * .3 }}><Icon size={small ? 22 : 35} strokeWidth={1.5} /></motion.span>)}</div>{!small && <p>{text}</p>}</div>; }
export function Reveal({ children, className = "", delay = 0 }: { children: ReactNode; className?: string; delay?: number }) { return <motion.div className={className} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .12 }} transition={{ duration: .55, delay }}>{children}</motion.div>; }
export function SectionHeading({ eyebrow, title, description, href, linkLabel = "View all products", light = false }: { eyebrow: string; title: string; description?: string; href?: string; linkLabel?: string; light?: boolean }) { return <div className={`section-heading ${light ? "light" : ""}`}><div><span className="eyebrow"><Sprout size={15} />{eyebrow}</span><h2>{title}</h2>{description && <p>{description}</p>}</div>{href && <Link className="text-link" href={href}>{linkLabel}<ArrowRight size={17} /></Link>}</div>; }
export function ProductSkeletons({ count = 4 }: { count?: number }) { return <div className="product-grid">{Array.from({ length: count }, (_, i) => <div key={i} className="product-skeleton"><div className="skeleton skeleton-image" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line short" /><div className="skeleton skeleton-line" /></div>)}</div>; }
export function EmptyState({ icon = "🧺", title, description, href = "/shop", linkLabel = "Explore the market" }: { icon?: string; title: string; description: string; href?: string; linkLabel?: string }) { return <div className="empty-state"><motion.span animate={{ rotate: [-5, 5, -5] }} transition={{ duration: 4, repeat: Infinity }}>{icon}</motion.span><h2>{title}</h2><p>{description}</p><Link className="button button-primary" href={href}>{linkLabel}<ArrowRight size={17} /></Link></div>; }
export { AnimatePresence, motion };
