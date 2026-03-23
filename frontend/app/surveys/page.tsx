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
import { surveysApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { SurveyListItem } from "@/lib/types";

export default function SurveysPage() {
  const [surveys, setSurveys] = useState<SurveyListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await surveysApi.list();
        setSurveys(data.items);
      } catch (error) {
        console.error("Failed to load surveys:", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const getTypeLabel = (type: SurveyListItem["survey_type"]) => {
    const labels: Record<string, string> = {
      quantitative: "Количественный",
      qualitative: "Качественный",
      mixed: "Смешанный",
    };
    return labels[type] || type;
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
          <h1 className="text-3xl font-bold">Опросы</h1>
          <p className="text-muted-foreground">Управление исследованиями</p>
        </div>
        <Link href="/surveys/new">
          <Button>Создать опрос</Button>
        </Link>
      </div>

      {surveys.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">У вас пока нет опросов</p>
            <Link href="/surveys/new">
              <Button>Создать первый опрос</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {surveys.map((survey) => (
            <Card key={survey.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{survey.title}</CardTitle>
                    <CardDescription>
                      Создан {formatDate(survey.created_at)}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={survey.is_active ? "secondary" : "outline"}>
                      {survey.is_active ? "Активен" : "Неактивен"}
                    </Badge>
                    <Badge variant="outline">{getTypeLabel(survey.survey_type)}</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Link href={`/surveys/${survey.id}`}>
                  <Button variant="outline" size="sm">
                    Подробнее
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
