import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Платформа симуляции опросов
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Многоагентная платформа для тестирования B2B-гипотез с использованием
            AI-персон для симуляции ответов реальных компаний
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Агенты</CardTitle>
              <CardDescription>
                AI-персоны ИП и ООО с реалистичными характеристиками
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Используйте готовых агентов с детальными профилями: тип
                собственности, отрасль, размер, болевые точки, стиль принятия
                решений.
              </p>
              <Link href="/agents">
                <Button variant="outline" className="w-full">
                  Просмотреть агентов
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Опросы</CardTitle>
              <CardDescription>
                Создание количественных и качественных исследований
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Конструируйте опросы с различными типами вопросов: шкалы Лайкерта,
                открытые вопросы, множественный выбор.
              </p>
              <Link href="/surveys">
                <Button variant="outline" className="w-full">
                  Управление опросами
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Симуляции</CardTitle>
              <CardDescription>
                Параллельное выполнение опросов множеством агентов
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Запускайте симуляции, следите за прогрессом в реальном времени,
                анализируйте результаты с помощью NLP.
              </p>
              <Link href="/simulations">
                <Button variant="outline" className="w-full">
                  Мои симуляции
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-12">
          <Link href="/dashboard">
            <Button size="lg">Перейти в дашборд</Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
