"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { authApi, llmConfigApi } from "@/lib/api";
import type { LLMProviderInfo } from "@/lib/types";

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [providers, setProviders] = useState<LLMProviderInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // User data
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [orgName, setOrgName] = useState("");

  // LLM config
  const [provider, setProvider] = useState("kimi");
  const [model, setModel] = useState("kimi-k2-07132k-preview");
  const [apiKey, setApiKey] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2000);

  useEffect(() => {
    async function loadProviders() {
      try {
        const data = await llmConfigApi.getProviders();
        setProviders(data.providers);
      } catch (err) {
        console.error("Failed to load providers:", err);
      }
    }
    loadProviders();
  }, []);

  // Update model when provider changes
  useEffect(() => {
    const selectedProvider = providers.find((p) => p.id === provider);
    if (selectedProvider) {
      setModel(selectedProvider.default_model);
    }
  }, [provider, providers]);

  const selectedProvider = providers.find((p) => p.id === provider);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authApi.register({
        email,
        password,
        full_name: fullName,
        organization_name: orgName,
        llm_provider: provider,
        llm_model: model,
        llm_api_key: apiKey,
        llm_temperature: temperature,
        llm_max_tokens: maxTokens,
      });

      // Auto-login after registration
      const loginResponse = await authApi.login(email, password);
      localStorage.setItem("access_token", loginResponse.access_token);
      localStorage.setItem("refresh_token", loginResponse.refresh_token);

      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Регистрация</CardTitle>
          <CardDescription>
            Создайте учетную запись и настройте LLM
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={`step-${step}`} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger
                value="step-1"
                onClick={() => setStep(1)}
                disabled={loading}
              >
                1. Профиль
              </TabsTrigger>
              <TabsTrigger
                value="step-2"
                onClick={() => setStep(2)}
                disabled={loading}
              >
                2. LLM Настройки
              </TabsTrigger>
            </TabsList>

            <form onSubmit={handleSubmit}>
              <TabsContent value="step-1" className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">ФИО</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    required
                    minLength={2}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Пароль</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    required
                    minLength={8}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Минимум 8 символов, заглавная буква, строчная буква и цифра
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium">Название организации</label>
                  <input
                    type="text"
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    required
                    minLength={2}
                  />
                </div>
                <Button
                  type="button"
                  className="w-full"
                  onClick={() => setStep(2)}
                >
                  Далее
                </Button>
              </TabsContent>

              <TabsContent value="step-2" className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">LLM Провайдер</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                  >
                    {providers.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                  {selectedProvider && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {selectedProvider.description}
                    </p>
                  )}
                </div>

                <div>
                  <label className="text-sm font-medium">Модель</label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                  >
                    {selectedProvider?.models.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium">API Key</label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md font-mono"
                    required
                    minLength={10}
                    placeholder="sk-..."
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Ваш API ключ будет сохранен securely и использоваться для всех LLM запросов
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Temperature</label>
                    <input
                      type="number"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      min={0}
                      max={2}
                      step={0.1}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Max Tokens</label>
                    <input
                      type="number"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      min={100}
                      max={8000}
                      step={100}
                    />
                  </div>
                </div>

                {selectedProvider?.docs_url && (
                  <p className="text-xs text-muted-foreground">
                    <a
                      href={selectedProvider.docs_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      Документация провайдера →
                    </a>
                  </p>
                )}

                {error && (
                  <div className="text-sm text-red-500">{error}</div>
                )}

                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    onClick={() => setStep(1)}
                    disabled={loading}
                  >
                    Назад
                  </Button>
                  <Button type="submit" className="flex-1" disabled={loading}>
                    {loading ? "Создание..." : "Создать аккаунт"}
                  </Button>
                </div>
              </TabsContent>
            </form>
          </Tabs>

          <div className="mt-4 text-center text-sm">
            Уже есть аккаунт?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Войти
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
