"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { authApi } from "@/lib/api";
import type { User } from "@/lib/types";

export function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await authApi.me();
        setUser(userData);
      } catch (error) {
        console.error("Failed to load user:", error);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  if (loading) {
    return (
      <nav className="border-b bg-background">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            Survey Platform
          </Link>
          <div className="animate-pulse h-8 w-24 bg-muted rounded"></div>
        </div>
      </nav>
    );
  }

  if (!user) {
    return (
      <nav className="border-b bg-background">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            Survey Platform
          </Link>
          <div className="flex gap-2">
            <Link href="/login">
              <Button variant="ghost" size="sm">Войти</Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Регистрация</Button>
            </Link>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-xl font-bold">
            Survey Platform
          </Link>
          <div className="hidden md:flex gap-4">
            <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
              Дашборд
            </Link>
            <Link href="/surveys" className="text-sm text-muted-foreground hover:text-foreground">
              Опросы
            </Link>
            <Link href="/simulations" className="text-sm text-muted-foreground hover:text-foreground">
              Симуляции
            </Link>
            <Link href="/agents" className="text-sm text-muted-foreground hover:text-foreground">
              Агенты
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground hidden md:inline">
            {user.full_name}
          </span>
          <Link href="/settings/llm">
            <Button variant="ghost" size="sm">⚙️</Button>
          </Link>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Выйти
          </Button>
        </div>
      </div>
    </nav>
  );
}
