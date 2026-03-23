"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { llmConfigApi } from "@/lib/api";
import type { LLMConfig, LLMProviderInfo } from "@/lib/types";

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
  {
    id: "ollama",
    name: "Ollama (Local)",
    description: "Локальные модели",
    models: ["llama3", "mistral", "codellama"],
    default_model: "llama3",
    requires_base_url: true,
    docs_url: "https://ollama.ai",
  },
];

export default function LLMSettingsPage() {
  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [providers, setProviders] = useState<LLMProviderInfo[]>(DEFAULT_PROVIDERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  // Form state
  const [provider, setProvider] = useState("kimi");
  const [model, setModel] = useState("kimi-k2-07132k-preview");
  const [apiKey, setApiKey] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2000);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        
        // Load providers from API
        try {
          const providersData = await llmConfigApi.getProviders();
          if (providersData.providers && providersData.providers.length > 0) {
            setProviders(providersData.providers);
          }
        } catch (err) {
          console.warn("Failed to load providers from API, using defaults", err);
          // Keep default providers
        }

        // Load user config
        try {
          const configData = await llmConfigApi.getMyConfig();
          if (configData) {
            setConfig(configData);
            setProvider(configData.provider);
            setModel(configData.model);
            setTemperature(configData.temperature);
            setMaxTokens(configData.max_tokens);
          }
        } catch (err) {
          console.log("No existing config found");
          // No config yet - that's ok for new users
        }
      } catch (err) {
        setError("Ошибка загрузки данных");
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Update model when provider changes
  useEffect(() => {
    const selectedProvider = providers.find((p) => p.id === provider);
    if (selectedProvider && !config) {
      setModel(selectedProvider.default_model);
    }
  }, [provider, providers, config]);

  const selectedProvider = providers.find((p) => p.id === provider);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTestResult(null);
    setError(null);

    try {
      const data = {
        provider,
        model,
        api_key: apiKey || undefined,
        temperature,
        max_tokens: maxTokens,
      };

      let newConfig;
      if (config) {
        newConfig = await llmConfigApi.updateMyConfig(data);
      } else {
        if (!apiKey) {
          setError("API ключ обязателен для создания конфигурации");
          setSaving(false);
          return;
        }
        newConfig = await llmConfigApi.createMyConfig({
          ...data,
          api_key: apiKey,
        });
      }

      setConfig(newConfig);
      setTestResult({ success: true, message: "Настройки сохранены успешно" });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка сохранения";
      setError(message);
      setTestResult({ success: false, message });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setError(null);

    try {
      const result = await llmConfigApi.testMyConfig();
      setTestResult({
        success: true,
        message: `Тест пройден! Модель: ${result.model}, Токенов: ${result.tokens_used}, Время: ${result.response_time_ms}ms`,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Тест не пройден";
      setTestResult({ success: false, message });
      setError(message);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/dashboard">
            <Button variant="outline" size="sm">← Назад</Button>
          </Link>
          <h1 className="text-3xl font-bold">Настройки LLM</h1>
        </div>
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-muted-foreground">Загрузка...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/dashboard">
          <Button variant="outline" size="sm">← Назад</Button>
        </Link>
        <h1 className="text-3xl font-bold">Настройки LLM</h1>
      </div>

      <div className="max-w-2xl">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Конфигурация LLM</CardTitle>
                <CardDescription>
                  Настройте параметры подключения к языковой модели
                </CardDescription>
              </div>
              {config && (
                <Badge variant={config.is_active ? "secondary" : "outline"}>
                  {config.is_active ? "Активно" : "Неактивно"}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="text-sm font-medium block mb-2">Провайдер</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                  disabled={saving}
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
                <label className="text-sm font-medium block mb-2">Модель</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                  disabled={saving}
                >
                  {selectedProvider?.models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium block mb-2">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md font-mono bg-background"
                  placeholder={config ? "•••••••• (оставьте пустым чтобы не менять)" : "sk-..."}
                  disabled={saving}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {config
                    ? "Оставьте пустым, чтобы сохранить текущий ключ"
                    : "Введите ваш API ключ"}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-2">Temperature</label>
                  <input
                    type="number"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md bg-background"
                    min={0}
                    max={2}
                    step={0.1}
                    disabled={saving}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    0 = детерминировано, 2 = креативно
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-2">Max Tokens</label>
                  <input
                    type="number"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md bg-background"
                    min={100}
                    max={8000}
                    step={100}
                    disabled={saving}
                  />
                </div>
              </div>

              {config && (
                <div className="text-sm text-muted-foreground border-t pt-4">
                  <p>Всего запросов: {config.total_requests}</p>
                  {config.last_used_at && (
                    <p>Последнее использование: {new Date(config.last_used_at).toLocaleString()}</p>
                  )}
                </div>
              )}

              {testResult && (
                <div
                  className={`text-sm p-3 rounded ${
                    testResult.success
                      ? "bg-green-50 text-green-700 border border-green-200"
                      : "bg-red-50 text-red-700 border border-red-200"
                  }`}
                >
                  {testResult.message}
                </div>
              )}

              <div className="flex gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleTest}
                  disabled={testing || saving || (!config && !apiKey)}
                >
                  {testing ? "Проверка..." : "Проверить подключение"}
                </Button>
                <Button type="submit" disabled={saving}>
                  {saving ? "Сохранение..." : "Сохранить"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {selectedProvider?.docs_url && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-sm">Документация</CardTitle>
            </CardHeader>
            <CardContent>
              <a
                href={selectedProvider.docs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline text-sm"
              >
                {selectedProvider.docs_url} →
              </a>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
