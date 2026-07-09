import type { MetadataRoute } from "next";
import { appConfig } from "@/config/app.config";

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: appConfig.url, changeFrequency: "daily", priority: 1 }];
}
