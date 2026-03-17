"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    inspirations: 0,
    insights: 0,
    drafts: 0,
    approved: 0,
    published: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const [inspirations, insights, content] = await Promise.all([
          api.getInspirations(),
          api.getInsights(),
          api.getContent(),
        ]);
        setStats({
          inspirations: inspirations.length,
          insights: insights.length,
          drafts: content.filter((c) => c.status === "draft").length,
          approved: content.filter((c) => c.status === "approved").length,
          published: content.filter((c) => c.status === "published").length,
        });
      } catch {
        // API may not be running yet
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const triggerInsights = async () => {
    try {
      const result = await api.triggerInsightExtraction();
      alert(`Extracted ${result.total_insights} insights`);
    } catch (e) {
      alert("Error extracting insights. Check that you have captured some inspirations first.");
    }
  };

  const triggerContent = async () => {
    try {
      const result = await api.triggerContentGeneration();
      alert(`Generated ${result.pieces_generated} content pieces`);
    } catch (e) {
      alert("Error generating content. Check backend logs for details.");
    }
  };

  const statCards = [
    { title: "Inspirations", value: stats.inspirations, color: "text-[#2BAAFF]", bg: "bg-[#F0F7FF]" },
    { title: "Insights", value: stats.insights, color: "text-[#F59E0B]", bg: "bg-[#FFFBF0]" },
    { title: "Drafts", value: stats.drafts, color: "text-[#54595F]", bg: "bg-[#F0F4F8]" },
    { title: "Approved", value: stats.approved, color: "text-[#2BAAFF]", bg: "bg-[#F0F7FF]" },
    { title: "Published", value: stats.published, color: "text-[#61CE70]", bg: "bg-[#F0FFF4]" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#212529]">Dashboard</h1>
          <p className="text-sm text-[#54595F] mt-1">Your content engine at a glance</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={triggerInsights}
            className="border-[#2BAAFF] text-[#2BAAFF] hover:bg-[#F0F7FF]"
          >
            Run Insight Miner
          </Button>
          <Button
            onClick={triggerContent}
            className="bg-[#2BAAFF] hover:bg-[#0082D8] text-white"
          >
            Generate Content
          </Button>
        </div>
      </div>

      {loading ? (
        <p className="text-[#54595F]">Loading...</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {statCards.map((stat) => (
            <Card key={stat.title} className={`${stat.bg} border-0 shadow-sm`}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-[#54595F]">{stat.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
