"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { agentsApi } from "@/lib/api";
import type { AgentListItem } from "@/lib/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentListItem[]>([]);
  const [filters, setFilters] = useState<{
    industries: string[];
    sizes: string[];
    regions: string[];
  }>({ industries: [], sizes: [], regions: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [agentsData, filtersData] = await Promise.all([
          agentsApi.list(),
          agentsApi.filters(),
        ]);
        setAgents(agentsData.items);
        setFilters(filtersData);
      } catch (error) {
        console.error("Failed to load agents:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const getSizeLabel = (size: string) => {
    const labels: Record<string, string> = {
      micro: "Микро",
      SMB: "Малый/Средний",
      mid: "Средний+",
      enterprise: "Крупный",
    };
    return labels[size] || size;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Загрузка...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Доступные агенты</h1>
      <p className="text-muted-foreground mb-8">
        AI-персоны для симуляции ответов реальных компаний
      </p>

      <div className="grid gap-4 mb-8">
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Отрасли:</span>
          {filters.industries.map((industry) => (
            <Badge key={industry} variant="secondary">
              {industry}
            </Badge>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Размеры:</span>
          {filters.sizes.map((size) => (
            <Badge key={size} variant="outline">
              {getSizeLabel(size)}
            </Badge>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <Card key={agent.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{agent.company_name}</CardTitle>
                  <CardDescription>{agent.industry}</CardDescription>
                </div>
                <Badge variant={agent.legal_type === "ООО" ? "default" : "secondary"}>
                  {agent.legal_type}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Регион:</span>
                  <span>{agent.region}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Размер:</span>
                  <span>{getSizeLabel(agent.size)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
