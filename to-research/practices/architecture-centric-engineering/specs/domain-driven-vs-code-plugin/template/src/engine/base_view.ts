// engine/base_view.ts — Base class for all server views
import * as fs from "fs";
import * as path from "path";
import type { Uri } from "vscode";

export class BaseView {
  protected _extensionUri: Uri;

  constructor(extensionUri: Uri) {
    this._extensionUri = extensionUri;
  }

  /** Load template from path (relative to extension) and replace {{key}} with data[key]. Content key passes through unescaped (HTML). */
  renderTemplate(relativePath: string, data: Record<string, unknown>): string {
    const templatePath = path.join(
      this._extensionUri.fsPath,
      ...relativePath.split("/")
    );
    const html = fs.readFileSync(templatePath, "utf8");
    return this.renderTemplateContent(html, data);
  }

  /** Replace {{key}} placeholders in template string. Content key passes through unescaped (HTML). */
  renderTemplateContent(html: string, data: Record<string, unknown>): string {
    let result = html;
    for (const [key, value] of Object.entries(data)) {
      const placeholder = `{{${key}}}`;
      const toInsert =
        key === "content" || key.endsWith("Html") ? String(value ?? "") : this._escapeHtml(value);
      result = result.split(placeholder).join(toInsert);
    }
    return result;
  }

  private _escapeHtml(value: unknown): string {
    if (value == null) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;");
  }
}
