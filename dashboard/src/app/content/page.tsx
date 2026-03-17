"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, type ContentPiece } from "@/lib/api";

const statusColors: Record<string, string> = {
  draft: "bg-gray-100 text-[#54595F] border-gray-200",
  approved: "bg-[#2BAAFF]/10 text-[#2BAAFF] border-[#2BAAFF]/20",
  published: "bg-[#61CE70]/10 text-[#61CE70] border-[#61CE70]/20",
  rejected: "bg-red-50 text-red-600 border-red-200",
  scheduled: "bg-amber-50 text-amber-600 border-amber-200",
};

const channelColors: Record<string, string> = {
  linkedin: "bg-[#0077B5] text-white",
  twitter: "bg-black text-white",
  blog: "bg-[#2BAAFF] text-white",
  email: "bg-[#61CE70] text-white",
};

const channelIcons: Record<string, string> = {
  linkedin: "in",
  twitter: "𝕏",
  blog: "B",
  email: "✉",
};

export default function ContentPage() {
  const [pieces, setPieces] = useState<ContentPiece[]>([]);
  const [channel, setChannel] = useState("all");

  useEffect(() => {
    api
      .getContent(channel === "all" ? undefined : channel)
      .then(setPieces)
      .catch(() => {});
  }, [channel]);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#212529]">Content</h1>
          <p className="text-sm text-[#54595F] mt-1">Review, edit, and publish your content</p>
        </div>
      </div>

      <Tabs value={channel} onValueChange={setChannel} className="mb-6">
        <TabsList className="bg-white border border-[#E2E8F0]">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="linkedin">LinkedIn</TabsTrigger>
          <TabsTrigger value="twitter">Twitter</TabsTrigger>
          <TabsTrigger value="blog">Blog</TabsTrigger>
          <TabsTrigger value="email">Email</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="space-y-3">
        {pieces.map((piece) => (
          <Link key={piece.id} href={`/content/${piece.id}`}>
            <Card className="bg-white border-[#E2E8F0] hover:shadow-md hover:border-[#2BAAFF]/30 transition-all cursor-pointer mb-3">
              <CardContent className="pt-4">
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold shrink-0 ${channelColors[piece.channel] || "bg-gray-200 text-gray-600"}`}>
                    {channelIcons[piece.channel] || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={`text-xs border ${statusColors[piece.status] || "bg-gray-100"}`}>
                        {piece.status}
                      </Badge>
                      <span className="text-xs text-[#54595F] capitalize">{piece.channel}</span>
                      {piece.suggested_post_time && (
                        <span className="text-xs text-[#54595F]/60">{piece.suggested_post_time}</span>
                      )}
                    </div>
                    <p className="text-sm font-semibold text-[#212529] mb-1">
                      {piece.selected_hook || piece.hooks?.[0]?.hook_text || "No hook"}
                    </p>
                    <p className="text-xs text-[#54595F] line-clamp-2">
                      {piece.body.slice(0, 200)}...
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}

        {pieces.length === 0 && (
          <div className="text-center py-16">
            <div className="w-16 h-16 rounded-full bg-[#F0F7FF] flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-[#2BAAFF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <p className="text-[#54595F] font-medium">No content yet</p>
            <p className="text-sm text-[#54595F]/60 mt-1">Click &ldquo;Generate Content&rdquo; on the Dashboard to create posts</p>
          </div>
        )}
      </div>
    </div>
  );
}
