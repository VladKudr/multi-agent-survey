"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { simulationsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { SimulationListItem } from "@/lib/types";

export default function SimulationsPage() {
  const [simulations, setSimulations] = useState<SimulationListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await simulationsApi.list();
        setSimulations(data.items);
      } catch (error) {
        console.error("Failed to load simulations:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const getStatusBadge = (status: SimulationListItem["status"]) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> =
      {
        pending: "outline",
        running: "default",
        completed: "secondary",
        failed: "destructive",
        cancelled: "outline",
      };
    return (
      <Badge variant={variants[status] || "default"}>
        {status === "pending" && "В очереди"}
        {status === "running" && "Выполняется"}
        {status === "completed" && "Завершено"}
        {status === "failed" && "Ошибка"}
        {status === "cancelled" && "Отменено"}
      </Badge>
    );
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
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Симуляции</h1>
          <p className="text-muted-foreground">История запусков и результаты</p>
        </div>
        <Link href="/simulations/new">
          <Button>Новая симуляция</Button>
        </Link>
      </div>

      {simulations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">У вас пока нет симуляций</p>
            <Link href="/simulations/new">
              <Button>Запустить первую симуляцию</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {simulations.map((sim) => (
            <Card key={sim.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{sim.name}</CardTitle>
                    <CardDescription>
                      Создана {formatDate(sim.created_at)}
                    </CardDescription>
                  </div>
                  {getStatusBadge(sim.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Прогресс:</span>
                    <span>
                      {sim.completed_agents} / {sim.total_agents} агентов
                    </span>
                  </div>
                  <Progress
                    value={(sim.completed_agents / sim.total_agents) * 100}
                  />
                  <Link href={`/simulations/${sim.id}`}>
                    <Button variant="outline" size="sm">
                      Подробнее
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
