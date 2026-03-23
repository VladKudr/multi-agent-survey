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
import { simulationsApi, surveysApi, authApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { SimulationListItem, SurveyListItem, User } from "@/lib/types";

export default function DashboardPage() {
  const [simulations, setSimulations] = useState<SimulationListItem[]>([]);
  const [surveys, setSurveys] = useState<SurveyListItem[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [simsData, surveysData, userData] = await Promise.all([
          simulationsApi.list({ limit: 5 }),
          surveysApi.list({ limit: 5 }),
          authApi.me(),
        ]);
        setSimulations(simsData.items);
        setSurveys(surveysData.items);
        setUser(userData);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const getStatusBadge = (status: SimulationListItem["status"]) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
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
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold">Дашборд</h1>
          {user && (
            <p className="text-muted-foreground">
              Добро пожаловать, {user.full_name}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Link href="/settings/llm">
            <Button variant="outline" size="sm">
              ⚙️ Настройки LLM
            </Button>
          </Link>
        </div>
      </div>

      {/* LLM Status Card */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>Конфигурация LLM</CardTitle>
              <CardDescription>Ваши настройки языковой модели</CardDescription>
            </div>
            {user?.llm_config ? (
              <Badge variant="secondary">Настроено</Badge>
            ) : (
              <Badge variant="destructive">Не настроено</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {user?.llm_config ? (
            <div className="grid md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Провайдер:</span>
                <p className="font-medium">{user.llm_config.provider}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Модель:</span>
                <p className="font-medium">{user.llm_config.model}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Temperature:</span>
                <p className="font-medium">{user.llm_config.temperature}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Запросов:</span>
                <p className="font-medium">{user.llm_config.total_requests}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-muted-foreground mb-4">
                LLM не настроен. Для запуска симуляций необходимо настроить API ключ.
              </p>
              <Link href="/settings/llm">
                <Button>Настроить LLM</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Последние симуляции</CardTitle>
              <CardDescription>Недавно запущенные симуляции</CardDescription>
            </div>
            <Link href="/simulations">
              <Button variant="outline" size="sm">
                Все симуляции
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {simulations.length === 0 ? (
              <p className="text-muted-foreground">Нет симуляций</p>
            ) : (
              <div className="space-y-4">
                {simulations.map((sim) => (
                  <div
                    key={sim.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{sim.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(sim.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      {getStatusBadge(sim.status)}
                      <p className="text-sm text-muted-foreground mt-1">
                        {sim.completed_agents}/{sim.total_agents} агентов
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Опросы</CardTitle>
              <CardDescription>Доступные опросы</CardDescription>
            </div>
            <Link href="/surveys">
              <Button variant="outline" size="sm">
                Все опросы
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {surveys.length === 0 ? (
              <p className="text-muted-foreground">Нет опросов</p>
            ) : (
              <div className="space-y-4">
                {surveys.map((survey) => (
                  <div
                    key={survey.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{survey.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {survey.survey_type === "quantitative" && "Количественный"}
                        {survey.survey_type === "qualitative" && "Качественный"}
                        {survey.survey_type === "mixed" && "Смешанный"}
                      </p>
                    </div>
                    <Badge variant={survey.is_active ? "secondary" : "outline"}>
                      {survey.is_active ? "Активен" : "Неактивен"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 flex gap-4">
        <Link href="/surveys/new">
          <Button>Создать опрос</Button>
        </Link>
        <Link href="/simulations/new">
          <Button variant="outline">Запустить симуляцию</Button>
        </Link>
      </div>
    </div>
  );
}
