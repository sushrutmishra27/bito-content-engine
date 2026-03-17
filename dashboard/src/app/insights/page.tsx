"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type Insight } from "@/lib/api";

const tagColors: Record<string, string> = {
  actionable: "bg-[#61CE70]/10 text-[#61CE70] border-[#61CE70]/20",
  trend: "bg-purple-50 text-purple-600 border-purple-200",
  "contrarian-take": "bg-red-50 text-red-600 border-red-200",
  "data-point": "bg-[#2BAAFF]/10 text-[#2BAAFF] border-[#2BAAFF]/20",
  story: "bg-orange-50 text-orange-600 border-orange-200",
};

function RelevanceStars({ score }: { score: number }) {
  return (
    <span className="text-amber-400 text-sm">
      {"★".repeat(score)}
      {"☆".repeat(5 - score)}
    </span>
  );
}

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [minRelevance, setMinRelevance] = useState(1);

  useEffect(() => {
    api.getInsights(undefined, minRelevance).then(setInsights).catch(() => {});
  }, [minRelevance]);

  const grouped = insights.reduce<Record<string, Insight[]>>((acc, insight) => {
    const key = insight.source_type;
    if (!acc[key]) acc[key] = [];
    acc[key].push(insight);
    return acc;
  }, {});

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#212529]">Insights</h1>
          <p className="text-sm text-[#54595F] mt-1">Key insights extracted from your sources</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#54595F]">Min relevance:</span>
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              onClick={() => setMinRelevance(n)}
              className={`text-lg ${n <= minRelevance ? "text-amber-400" : "text-gray-300"}`}
            >
              ★
            </button>
          ))}
        </div>
      </div>

      {Object.entries(grouped).map(([sourceType, items]) => (
        <div key={sourceType} className="mb-8">
          <h2 className="text-lg font-semibold text-[#212529] mb-4 capitalize">
            {sourceType} ({items.length})
          </h2>
          <div className="space-y-3">
            {items.map((insight) => (
              <Card key={insight.id} className="bg-white border-[#E2E8F0] shadow-sm">
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-sm text-[#212529] mb-2">{insight.insight_text}</p>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {insight.tags.map((tag) => (
                          <Badge key={tag} className={`text-xs border ${tagColors[tag] || "bg-gray-50 text-gray-600"}`}>
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      {insight.suggested_angles.length > 0 && (
                        <p className="text-xs text-[#54595F]">
                          Angles: {insight.suggested_angles.join(" • ")}
                        </p>
                      )}
                    </div>
                    <RelevanceStars score={insight.relevance_score} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}

      {insights.length === 0 && (
        <div className="text-center py-16">
          <div className="w-16 h-16 rounded-full bg-[#FFFBF0] flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p className="text-[#54595F] font-medium">No insights yet</p>
          <p className="text-sm text-[#54595F]/60 mt-1">Run the Insight Miner from the Dashboard after capturing some inspirations</p>
        </div>
      )}
    </div>
  );
}
