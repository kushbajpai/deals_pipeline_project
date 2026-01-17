import React, { useState, useEffect } from "react";
import { dealsAPI } from "../../api/deals.api";
import type { ICMemo } from "../../types";
import "../../styles/ICMemo.css";

interface ICMemoEditorProps {
  dealId: number;
  onSave?: () => void;
  onActivityClick?: () => void;
}

export const ICMemoEditor: React.FC<ICMemoEditorProps> = ({ dealId, onSave, onActivityClick }) => {
  const [memo, setMemo] = useState<ICMemo | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [editData, setEditData] = useState({
    summary: "",
    market: "",
    product: "",
    traction: "",
    risks: "",
    open_questions: "",
  });

  // Sections to render
  const MEMO_SECTIONS = [
    { key: "summary", label: "Executive Summary" },
    { key: "market", label: "Market Analysis" },
    { key: "product", label: "Product Description" },
    { key: "traction", label: "Traction Metrics" },
    { key: "risks", label: "Identified Risks" },
    { key: "open_questions", label: "Open Questions" },
  ];

  // Load memo on mount
  useEffect(() => {
    loadMemo();
  }, [dealId]);

  // Update edit data when memo loads
  useEffect(() => {
    if (memo && isEditing) {
      setEditData({
        summary: memo.summary || "",
        market: memo.market || "",
        product: memo.product || "",
        traction: memo.traction || "",
        risks: memo.risks || "",
        open_questions: memo.open_questions || "",
      });
    }
  }, [memo, isEditing]);

  const loadMemo = async () => {
    try {
      const response = await dealsAPI.getICMemo(dealId);
      setMemo(response);
    } catch (error) {
      console.log("No existing memo for this deal yet");
    }
  };

  const handleEditChange = (field: string, value: string) => {
    setEditData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await dealsAPI.saveICMemo(dealId, editData);
      setMemo(response);
      setIsEditing(false);
      onSave?.();
      console.log("IC Memo saved successfully");
    } catch (error) {
      console.error("Error saving memo:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  if (!memo && !isEditing) {
    return (
      <div className="ic-memo-container">
        <div className="ic-memo-empty">
          <h3>No IC Memo Yet</h3>
          <p>Create a structured analysis for this deal</p>
          <button
            className="btn btn-primary"
            onClick={() => setIsEditing(true)}
          >
            Create IC Memo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ic-memo-container">
      <div className="ic-memo-header">
        <div className="ic-memo-title">
          <h2>IC Memo</h2>
          {memo && <span className="version-badge">v{memo.current_version}</span>}
        </div>
        <div className="ic-memo-actions">
          {!isEditing && memo && (
            <>
              <button
                className="btn btn-secondary"
                onClick={() => setShowVersionHistory(!showVersionHistory)}
              >
                {showVersionHistory ? "Hide" : "Show"} Version History
              </button>
              <button
                className="btn btn-primary"
                onClick={() => setIsEditing(true)}
              >
                Edit Memo
              </button>
            </>
          )}
          {isEditing && (
            <>
              <button
                className="btn btn-success"
                onClick={handleSave}
                disabled={isSaving}
              >
                {isSaving ? "Saving..." : "Save Memo"}
              </button>
              <button
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </div>

      {showVersionHistory && memo && (
        <VersionHistory dealId={dealId} currentVersion={memo.current_version} />
      )}

      <div className="ic-memo-content">
        {isEditing ? (
          <div className="ic-memo-editor">
            {MEMO_SECTIONS.map(({ key, label }) => (
              <div key={key} className="memo-section-edit">
                <label htmlFor={`memo-${key}`}>{label}</label>
                <textarea
                  id={`memo-${key}`}
                  value={editData[key as keyof typeof editData]}
                  onChange={(e) => handleEditChange(key, e.target.value)}
                  placeholder={`Enter ${label.toLowerCase()}...`}
                  rows={5}
                />
              </div>
            ))}
          </div>
        ) : memo ? (
          <div className="ic-memo-view">
            {MEMO_SECTIONS.map(({ key, label }) => (
              <div key={key} className="memo-section-view">
                <h3>{label}</h3>
                <div className="memo-section-content">
                  {memo[key as keyof ICMemo] ? (
                    <p>{memo[key as keyof ICMemo]}</p>
                  ) : (
                    <p className="empty-section">No content</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
};

interface VersionHistoryProps {
  dealId: number;
  currentVersion: number;
}

const VersionHistory: React.FC<VersionHistoryProps> = ({ dealId, currentVersion }) => {
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadVersionHistory();
  }, [dealId]);

  const loadVersionHistory = async () => {
    setLoading(true);
    try {
      const response = await dealsAPI.getICMemoHistory(dealId);
      setVersions(response.versions);
    } catch (error) {
      console.error("Error loading version history:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewVersion = async (versionNum: number) => {
    try {
      const response = await dealsAPI.getICMemoVersion(dealId, versionNum);
      setSelectedVersion(response);
    } catch (error) {
      console.error("Error loading version:", error);
    }
  };

  const MEMO_SECTIONS = [
    { key: "summary", label: "Executive Summary" },
    { key: "market", label: "Market Analysis" },
    { key: "product", label: "Product Description" },
    { key: "traction", label: "Traction Metrics" },
    { key: "risks", label: "Identified Risks" },
    { key: "open_questions", label: "Open Questions" },
  ];

  if (loading) {
    return <div className="version-history-container">Loading version history...</div>;
  }

  return (
    <div className="version-history-container">
      <div className="version-history-list">
        <h3>Version History</h3>
        {versions.map((version) => (
          <div
            key={version.id}
            className={`version-item ${selectedVersion?.id === version.id ? "selected" : ""}`}
          >
            <div className="version-header">
              <span className="version-number">v{version.version_number}</span>
              <span className="version-date">
                {new Date(version.created_at).toLocaleString()}
              </span>
            </div>
            {version.change_summary && (
              <div className="version-change">
                {version.change_summary}
              </div>
            )}
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => handleViewVersion(version.version_number)}
            >
              View
            </button>
          </div>
        ))}
      </div>

      {selectedVersion && (
        <div className="version-detail">
          <h3>Version {selectedVersion.version_number} (Read-only)</h3>
          <div className="version-metadata">
            <span className="metadata-item">
              Created: {new Date(selectedVersion.created_at).toLocaleString()}
            </span>
            {selectedVersion.change_summary && (
              <span className="metadata-item">
                Changes: {selectedVersion.change_summary}
              </span>
            )}
          </div>
          <div className="ic-memo-view">
            {MEMO_SECTIONS.map(({ key, label }) => (
              <div key={key} className="memo-section-view">
                <h4>{label}</h4>
                <div className="memo-section-content">
                  {selectedVersion[key] ? (
                    <p>{selectedVersion[key]}</p>
                  ) : (
                    <p className="empty-section">No content</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ICMemoEditor;
