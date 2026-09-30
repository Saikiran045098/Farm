import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowRight, ChevronRight, Sprout } from "lucide-react";
import { stories } from "@/data/catalog";
import { Newsletter } from "@/components/homepage";
import type { Metadata } from "next";
export function generateStaticParams() { return stories.map(s => ({ slug: s.slug })); }
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> { const { slug } = await params; const story = stories.find(s => s.slug === slug); return { title: story?.title || "Village story", description: story?.intro, openGraph: story ? { images: [story.image] } : undefined }; }
export default async function StoryPage({ params }: { params: Promise<{ slug: string }> }) { const { slug } = await params; const story = stories.find(s => s.slug === slug); if (!story) notFound(); return <main><article className="container article"><div className="breadcrumbs"><Link href="/">Home</Link><ChevronRight size={11} /><Link href="/stories">Village diary</Link><ChevronRight size={11} /><span>A little story</span></div><span className="eyebrow"><Sprout size={14} />{story.category}</span><h1>{story.title}</h1><p className="article-intro">{story.intro}</p><div className="article-meta"><span>By the FarmBuddy village family</span><span>{story.minutes} minute read</span><span>Telangana, India</span></div><div className="article-hero"><Image src={story.image} alt={story.title} fill priority sizes="(max-width: 700px) 90vw, 820px" /></div><div className="article-body">{story.paragraphs.map((p, i) => <p key={i}>{p}</p>)}<div className="article-back"><Link className="text-link" href="/stories"><ArrowLeft size={14} />Back to our village diary</Link><Link className="text-link" href="/shop">Bring a little goodness home<ArrowRight size={14} /></Link></div></div></article><Newsletter /></main>; }
