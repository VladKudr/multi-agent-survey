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

// Default providers if API fails
const DEFAULT_PROVIDERS: LLMProviderInfo[] = [
  {
    id: "kimi",
    name: "Kimi (Moonshot AI)",
    description: "Kimi API от Moonshot AI",
    models: ["kimi-k2-07132k-preview", "kimi-latest", "kimi-k1.5"],
    default_model: "kimi-k2-07132k-preview",
    requires_base_url: false,
    docs_url: "https://platform.moonshot.cn/docs",
  },
  {
    id: "openai",
    name: "OpenAI",
    description: "OpenAI GPT модели",
    models: ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"],
    default_model: "gpt-4o",
    requires_base_url: false,
    docs_url: "https://platform.openai.com/docs",
  },
  {
    id: "anthropic",
    name: "Anthropic Claude",
    description: "Anthropic Claude модели",
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    default_model: "claude-3-sonnet",
    requires_base_url: false,
    docs_url: "https://docs.anthropic.com",
  },
];

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [providers, setProviders] = useState<LLMProviderInfo[]>(DEFAULT_PROVIDERS);
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
        if (data.providers && data.providers.length > 0) {
          setProviders(data.providers);
        }
      } catch (err) {
        console.warn("Failed to load providers from API, using defaults", err);
        // Keep default providers
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
                    placeholder="Иван Иванов"
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
                    placeholder="ivan@example.com"
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
                    placeholder="Минимум 8 символов"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Минимум 8 символов, заглавная, строчная буква и цифра
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
                    placeholder="ООО Ромашка"
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
                    className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
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
                    className="w-full mt-1 px-3 py-2 border rounded-md bg-background"
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
                    Получите ключ на {selectedProvider?.docs_url}
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

                {error && (
                  <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
                    {error}
                  </div>
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
