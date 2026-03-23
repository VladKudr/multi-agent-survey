"use client";

import { useEffect, useState } from "react";
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
import { Badge } from "@/components/ui/badge";
import { llmConfigApi } from "@/lib/api";
import type { LLMConfig, LLMProviderInfo } from "@/lib/types";

export default function LLMSettingsPage() {
  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [providers, setProviders] = useState<LLMProviderInfo[]>([]);
  const [loading, setLoading] = useState(true);
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
        const [configData, providersData] = await Promise.all([
          llmConfigApi.getMyConfig().catch(() => null),
          llmConfigApi.getProviders(),
        ]);
        setConfig(configData);
        setProviders(providersData.providers);

        if (configData) {
          setProvider(configData.provider);
          setModel(configData.model);
          setTemperature(configData.temperature);
          setMaxTokens(configData.max_tokens);
        }
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const selectedProvider = providers.find((p) => p.id === provider);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTestResult(null);

    try {
      const data = {
        provider,
        model,
        api_key: apiKey || undefined,
        temperature,
        max_tokens: maxTokens,
      };

      if (config) {
        await llmConfigApi.updateMyConfig(data);
      } else {
        await llmConfigApi.createMyConfig({
          ...data,
          api_key: apiKey,
        });
      }

      // Reload config
      const newConfig = await llmConfigApi.getMyConfig();
      setConfig(newConfig);
      setTestResult({ success: true, message: "Настройки сохранены" });
    } catch (err) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : "Ошибка сохранения",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      const result = await llmConfigApi.testMyConfig();
      setTestResult({
        success: true,
        message: `Тест пройден! Модель: ${result.model}, Токенов: ${result.tokens_used}, Время: ${result.response_time_ms}ms`,
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : "Тест не пройден",
      });
    } finally {
      setTesting(false);
    }
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
      <div className="flex items-center gap-4 mb-8">
        <Link href="/dashboard">
          <Button variant="outline" size="sm">← Назад</Button>
        </Link>
        <h1 className="text-3xl font-bold">Настройки LLM</h1>
      </div>

      <div className="max-w-2xl">
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
                <label className="text-sm font-medium">Провайдер</label>
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
                  placeholder={config ? "•••••••• (оставьте пустым чтобы не менять)" : "sk-..."}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {config
                    ? "Оставьте пустым, чтобы сохранить текущий ключ"
                    : "Введите ваш API ключ"}
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
                  <p className="text-xs text-muted-foreground mt-1">
                    0 = детерминировано, 2 = максимально креативно
                  </p>
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
                      ? "bg-green-50 text-green-700"
                      : "bg-red-50 text-red-700"
                  }`}
                >
                  {testResult.message}
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleTest}
                  disabled={testing || (!config && !apiKey)}
                >
                  {testing ? "Тестирование..." : "Проверить подключение"}
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
