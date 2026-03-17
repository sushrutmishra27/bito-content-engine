"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, type Inspiration } from "@/lib/api";

const categories = [
  { value: "all", label: "All Categories" },
  { value: "product-insight", label: "Product Insight" },
  { value: "competitor-intel", label: "Competitor Intel" },
  { value: "industry-trend", label: "Industry Trend" },
  { value: "content-idea", label: "Content Idea" },
  { value: "engineering", label: "Engineering" },
  { value: "customer-story", label: "Customer Story" },
];

const categoryColors: Record<string, string> = {
  "product-insight": "bg-[#2BAAFF]/10 text-[#2BAAFF] border-[#2BAAFF]/20",
  "competitor-intel": "bg-red-50 text-red-600 border-red-200",
  "industry-trend": "bg-purple-50 text-purple-600 border-purple-200",
  "content-idea": "bg-[#61CE70]/10 text-[#61CE70] border-[#61CE70]/20",
  engineering: "bg-amber-50 text-amber-600 border-amber-200",
  "customer-story": "bg-orange-50 text-orange-600 border-orange-200",
};

export default function InspirationsPage() {
  const [inspirations, setInspirations] = useState<Inspiration[]>([]);
  const [category, setCategory] = useState("all");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    api
      .getInspirations(category === "all" ? undefined : category)
      .then(setInspirations)
      .catch(() => {});
  }, [category]);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#212529]">Inspirations</h1>
          <p className="text-sm text-[#54595F] mt-1">Content captured from the web</p>
        </div>
        <Select value={category} onValueChange={(v) => v && setCategory(v)}>
          <SelectTrigger className="w-48 bg-white border-[#E2E8F0]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {categories.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>
                {cat.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {inspirations.map((insp) => (
          <Card
            key={insp.id}
            className="bg-white border-[#E2E8F0] cursor-pointer hover:shadow-md hover:border-[#2BAAFF]/30 transition-all"
            onClick={() => setExpanded(expanded === insp.id ? null : insp.id)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="text-sm font-semibold text-[#212529] leading-tight">
                  {insp.title}
                </CardTitle>
                <Badge className={`text-xs border ${categoryColors[insp.category] || "bg-gray-50 text-gray-600"}`}>
                  {insp.category}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {insp.note && (
                <p className="text-sm text-[#54595F] mb-2 italic">&ldquo;{insp.note}&rdquo;</p>
              )}
              <p className="text-xs text-[#54595F]/60 mb-2">
                {new Date(insp.captured_at).toLocaleDateString()}
              </p>
              {expanded === insp.id ? (
                <div className="mt-3 pt-3 border-t border-[#E2E8F0]">
                  <p className="text-sm text-[#212529] whitespace-pre-wrap">
                    {insp.content_markdown.slice(0, 1000)}
                    {insp.content_markdown.length > 1000 && "..."}
                  </p>
                  <a
                    href={insp.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#2BAAFF] text-xs mt-2 block hover:underline"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View original
                  </a>
                </div>
              ) : (
                <p className="text-xs text-[#54595F]/40">Click to expand</p>
              )}
            </CardContent>
          </Card>
        ))}

        {inspirations.length === 0 && (
          <div className="col-span-full text-center py-16">
            <div className="w-16 h-16 rounded-full bg-[#F0F7FF] flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-[#2BAAFF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-[#54595F] font-medium">No inspirations yet</p>
            <p className="text-sm text-[#54595F]/60 mt-1">Use the Chrome extension to capture content from the web</p>
          </div>
        )}
      </div>
    </div>
  );
}
