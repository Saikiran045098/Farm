import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, Sprout } from "lucide-react";
import { stories } from "@/data/catalog";
import { Reveal } from "@/components/ui";
import { Newsletter } from "@/components/homepage";
export const metadata = { title: "Stories From Our Village", description: "Discover native Telangana grains, traditional Sarvapindi recipes, fresh milk, and the stories behind our farming community." };
export default function StoriesPage() { return <main><section className="container"><div className="page-heading"><span className="eyebrow"><Sprout size={14} />RECIPES, ROOTS, AND LITTLE VILLAGE STORIES</span><h1>From our village diary.</h1><p>A little wisdom from our fields. A familiar flavour from our kitchens. Pull up a chair and stay a while.</p></div><div className="story-grid" style={{ paddingBottom: 60 }}>{stories.map((story, i) => <Reveal key={story.slug} delay={i * .04}><Link className="story-card" href={`/stories/${story.slug}`}><div className="story-photo"><Image src={story.image} alt={story.title} fill sizes="(max-width: 700px) 90vw, 33vw" /><span>{story.minutes} MIN READ</span></div><div className="story-content"><span className="eyebrow">{story.category}</span><h3>{story.title}</h3><p>{story.intro}</p><span className="text-link">A little more of the story<ArrowUpRight size={15} /></span></div></Link></Reveal>)}</div></section><Newsletter /></main>; }
