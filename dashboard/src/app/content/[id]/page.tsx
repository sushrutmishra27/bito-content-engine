"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, type ContentPiece } from "@/lib/api";

export default function ContentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [piece, setPiece] = useState<ContentPiece | null>(null);
  const [body, setBody] = useState("");
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (params.id) {
      api
        .getContentById(params.id as string)
        .then((data) => {
          setPiece(data);
          setBody(data.body);
          setStatus(data.status);
        })
        .catch(() => {});
    }
  }, [params.id]);

  const handleSave = async () => {
    if (!piece) return;
    setSaving(true);
    try {
      const updated = await api.updateContent(piece.id, { body, status });
      setPiece(updated);
    } finally {
      setSaving(false);
    }
  };

  const handleSelectHook = async (hookId: string) => {
    if (!piece) return;
    await api.selectHook(piece.id, hookId);
    const updated = await api.getContentById(piece.id);
    setPiece(updated);
  };

  if (!piece) {
    return <p className="text-[#54595F]">Loading...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="text-[#54595F] hover:text-[#2BAAFF] transition-colors"
          >
            &larr; Back
          </button>
          <h1 className="text-2xl font-bold text-[#212529] capitalize">{piece.channel} Post</h1>
          <Badge className="bg-[#F0F7FF] text-[#2BAAFF] border border-[#2BAAFF]/20">{piece.category}</Badge>
        </div>
        <div className="flex items-center gap-3">
          <Select value={status} onValueChange={(v) => v && setStatus(v)}>
            <SelectTrigger className="w-36 bg-white border-[#E2E8F0]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="approved">Approved</SelectItem>
              <SelectItem value="published">Published</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleSave}
            disabled={saving}
            className="bg-[#2BAAFF] hover:bg-[#0082D8] text-white"
          >
            {saving ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Content editor */}
        <div className="lg:col-span-2">
          <Card className="bg-white border-[#E2E8F0] shadow-sm">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-[#54595F]">Content Body</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                className="min-h-[400px] bg-[#F5FBFF] border-[#E2E8F0] text-[#212529] text-sm"
              />
              <p className="text-xs text-[#54595F]/60 mt-2">
                {body.length} characters
                {piece.channel === "twitter" && body.length > 280 && (
                  <span className="text-red-500 ml-2">Exceeds 280 char limit</span>
                )}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Hook selector */}
        <div>
          <Card className="bg-white border-[#E2E8F0] shadow-sm">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-[#54595F]">
                Hook Options ({piece.hooks.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {piece.hooks.map((hook) => (
                  <button
                    key={hook.id}
                    onClick={() => handleSelectHook(hook.id)}
                    className={`w-full text-left p-3 rounded-xl text-sm transition-all ${
                      hook.is_selected
                        ? "bg-[#2BAAFF]/10 border-2 border-[#2BAAFF] text-[#212529]"
                        : "bg-[#F5FBFF] border border-[#E2E8F0] text-[#54595F] hover:border-[#2BAAFF]/40"
                    }`}
                  >
                    <span className="text-xs text-[#54595F]/60 block mb-1">#{hook.rank}</span>
                    {hook.hook_text}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {piece.suggested_post_time && (
            <Card className="bg-white border-[#E2E8F0] shadow-sm mt-4">
              <CardContent className="pt-4">
                <p className="text-xs text-[#54595F]">Suggested Post Time</p>
                <p className="text-sm font-medium text-[#212529]">{piece.suggested_post_time}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
