"use client";
import { Sprout, ArrowRight } from "lucide-react";
import Link from "next/link";
export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) { return <main className="error-page"><div className="error-content"><Sprout size={47} strokeWidth={1.3} /><h1>Our village needs a little moment.</h1><p>Something didn’t load quite right. Your goodness is still here — let’s give it another try.</p><button className="button button-primary" onClick={reset}>Try again<ArrowRight size={15} /></button><p><Link className="text-link" href="/">Back to the village</Link></p></div></main>; }
