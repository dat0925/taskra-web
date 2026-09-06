/* ============================================================================
 * Taskra オンラインマニュアル用 デモデータ注入スクリプト
 * ----------------------------------------------------------------------------
 * app.taskra.jp を開いた状態のコンソールで実行すると、
 * 画面上の状態（S）だけをデモ用データに差し替える。
 *
 * ■ DBには一切書き込まない
 *   - dbPut / dbDel を no-op に差し替えるため、誤操作しても保存されない
 *   - loadAll を no-op に差し替えるため、120秒ポーリングで実データに戻らない
 *   - 元に戻すにはページをリロードするだけ（location.reload()）
 *
 * ■ 個人情報の秘匿
 *   - 表示名を「Taskra ユーザー」、メールを user@example.com に置換する
 *
 * 使い方:  このファイルの中身をそのまま evaluate する
 *          → TaskraDemo.on()  で注入 / TaskraDemo.view('nextview') で遷移
 * ========================================================================== */
(function () {
  'use strict';

  // ---- 日付ヘルパー（今日からの相対日数 → YYYY-MM-DD） ----
  // 注意: toISOString() は UTC を返すため、JST の 09:00 より前に実行すると
  //       日付が1日前にずれる。必ずローカル日付で組み立てる。
  const D = (n) => {
    const d = new Date();
    d.setDate(d.getDate() + n);
    const p = (x) => String(x).padStart(2, '0');
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
  };
  const TS = (n) => {
    const d = new Date();
    d.setDate(d.getDate() + n);
    return d.toISOString();
  };

  const WS_ID = 'demo-ws-1';

  // ---- プロジェクト（この並び順が Next ビューの並び順になる） ----
  const projects = [
    { id: 'p1', name: 'Webサイトリニューアル', color: '#3b82f6' },
    { id: 'p2', name: '新サービスの企画',       color: '#8b5cf6' },
    { id: 'p3', name: '採用活動 2026秋',        color: '#10b981' },
    { id: 'p4', name: '月次レポート作成',       color: '#f59e0b' },
    { id: 'p5', name: '社内AI勉強会',           color: '#ef4444' },
    { id: 'p6', name: '展示会の準備',           color: '#06b6d4', workspaceId: WS_ID },
  ].map((p, i) => ({
    type: 'list',
    status: 'active',
    reviewEveryDays: 7,
    nextReviewAt: i < 3 ? D(-1) : D(5),   // 先頭3件だけ Review の対象に出す
    order: (i + 1) * 1000,
    createdAt: TS(-60),
    updatedAt: TS(-2),
    workspaceId: null,
    ...p,
  }));

  // ---- タグ ----
  const tags = [
    { id: 'g1', name: '打ち合わせ', color: '#0ea5e9' },
    { id: 'g2', name: '提出物',     color: '#f43f5e' },
    { id: 'g3', name: '要確認',     color: '#f59e0b' },
    { id: 'g4', name: 'アイデア',   color: '#8b5cf6' },
  ].map((t, i) => ({ status: 'active', order: (i + 1) * 1000, ...t }));

  // ---- タスク ----
  // status: 'inbox'（未整理） / 'active'（プロジェクト所属） / 'completed'
  // startAt が未来のタスク = 「開始前」。Next の「現在」フィルタで飛ばされる
  const T = (o) => ({
    id: o.id,
    title: o.title,
    notes: o.notes || '',
    status: o.status || 'active',
    projectId: o.projectId || null,
    parentTaskId: o.parentTaskId || null,
    sectionId: null,
    tagIds: o.tagIds || [],
    priority: o.priority || 4,
    dueAt: o.dueAt !== undefined ? o.dueAt : null,
    startAt: o.startAt !== undefined ? o.startAt : null,
    plannedStartAt: o.startAt !== undefined ? o.startAt : null,
    startTime: o.startTime || null,
    deadlineAt: null,
    repeatRule: o.repeatRule || null,
    reminderAt: null,
    flagged: !!o.flagged,
    assigneeId: o.assigneeId || null,
    order: o.order || 1000,
    createdAt: o.createdAt || TS(-20),
    updatedAt: o.updatedAt || TS(-1),
    completedAt: o.completedAt || null,
  });

  const tasks = [
    // ===== p1 Webサイトリニューアル =====
    T({ id: 't101', projectId: 'p1', order: 1000, title: '現行サイトの課題を洗い出す',
        dueAt: D(-2), startAt: D(-10), priority: 1, flagged: true, tagIds: ['g3'] }),
    T({ id: 't102', projectId: 'p1', order: 2000, title: 'ワイヤーフレームを作成する',
        dueAt: D(0), startAt: D(-3), priority: 2,
        notes: 'トップ・商品一覧・お問い合わせの3画面から着手する。' }),
    T({ id: 't102a', projectId: 'p1', parentTaskId: 't102', order: 2100, title: 'トップページ',
        dueAt: D(0), startAt: D(-3) }),
    T({ id: 't102b', projectId: 'p1', parentTaskId: 't102', order: 2200, title: '商品一覧ページ',
        dueAt: D(1), startAt: D(0) }),
    T({ id: 't103', projectId: 'p1', order: 3000, title: 'デザイン案をレビューする',
        dueAt: D(4), startAt: D(2), tagIds: ['g1'] }),
    T({ id: 't104', projectId: 'p1', order: 4000, title: '制作会社に見積もりを依頼する',
        dueAt: D(7), startAt: D(5), tagIds: ['g2'] }),
    T({ id: 't105', projectId: 'p1', order: 500, title: 'キックオフMTGを実施する',
        status: 'completed', dueAt: D(-14), startAt: D(-14),
        completedAt: TS(-14), tagIds: ['g1'] }),

    // ===== p2 新サービスの企画 =====
    T({ id: 't201', projectId: 'p2', order: 1000, title: '競合サービスを調査する',
        dueAt: D(0), startAt: D(-5), priority: 2, flagged: true, tagIds: ['g3'] }),
    T({ id: 't202', projectId: 'p2', order: 2000, title: '企画書のドラフトを書く',
        dueAt: D(2), startAt: D(0), tagIds: ['g4'] }),
    T({ id: 't203', projectId: 'p2', order: 3000, title: '社内レビューを受ける',
        dueAt: D(5), startAt: D(3), tagIds: ['g1'] }),
    T({ id: 't204', projectId: 'p2', order: 500, title: 'アイデアを3案に絞る',
        status: 'completed', dueAt: D(-6), startAt: D(-9), completedAt: TS(-6) }),

    // ===== p3 採用活動 2026秋 =====
    T({ id: 't301', projectId: 'p3', order: 1000, title: '求人票を更新する',
        dueAt: D(-1), startAt: D(-7), priority: 2 }),
    T({ id: 't302', projectId: 'p3', order: 2000, title: '一次面接の日程を調整する',
        dueAt: D(1), startAt: D(0), tagIds: ['g1'] }),
    T({ id: 't303', projectId: 'p3', order: 3000, title: '内定者へ連絡する',
        dueAt: D(9), startAt: D(8) }),

    // ===== p4 月次レポート作成 =====
    // ★先頭タスクの開始日が未来 → 「現在」フィルタONのとき Next には2件目が出る
    T({ id: 't401', projectId: 'p4', order: 1000, title: '8月の数値を集計する',
        dueAt: D(3), startAt: D(1), tagIds: ['g2'] }),
    T({ id: 't402', projectId: 'p4', order: 2000, title: '前月比のコメントを書く',
        dueAt: D(4), startAt: D(0) }),
    T({ id: 't403', projectId: 'p4', order: 3000, title: '経営会議で報告する',
        dueAt: D(6), startAt: D(6), tagIds: ['g1', 'g2'] }),

    // ===== p5 社内AI勉強会 =====
    T({ id: 't501', projectId: 'p5', order: 1000, title: '開催日を決める',
        dueAt: D(2), startAt: D(-1), tagIds: ['g1'], repeatRule: null }),
    T({ id: 't502', projectId: 'p5', order: 2000, title: '当日の資料を準備する',
        dueAt: D(8), startAt: D(3) }),

    // ===== p6 展示会の準備（共有プロジェクト・Assigned 用） =====
    T({ id: 't601', projectId: 'p6', order: 1000, title: 'ブース什器を手配する',
        dueAt: D(10), startAt: D(0), assigneeId: '__ME__' }),
    T({ id: 't602', projectId: 'p6', order: 2000, title: '配布資料を印刷する',
        dueAt: D(12), startAt: D(2), assigneeId: '__ME__', tagIds: ['g2'] }),
    T({ id: 't603', projectId: 'p6', order: 3000, title: '当日のシフトを組む',
        dueAt: D(11), startAt: D(1) }),

    // ===== Inbox（プロジェクト未設定・期限なし＝Review の「停滞タスク」にも出る） =====
    T({ id: 'i01', status: 'inbox', order: 1000, title: '請求書の発行方法を確認する',
        dueAt: null, startAt: null, updatedAt: TS(-12) }),
    T({ id: 'i02', status: 'inbox', order: 2000, title: 'ノートPCの買い替えを申請する',
        dueAt: null, startAt: null, updatedAt: TS(-9) }),
    T({ id: 'i03', status: 'inbox', order: 3000, title: '読みたい本：チームトポロジー',
        dueAt: null, startAt: null, updatedAt: TS(-30), tagIds: ['g4'] }),
    T({ id: 'i04', status: 'inbox', order: 4000, title: '来期の予算枠を確認する',
        dueAt: D(0), startAt: D(0), flagged: true }),
  ];

  // ---- ノート ----
  const notes = [
    { id: 'n1', title: 'サービス名の候補メモ',
      body: '・Taskra（現行）\n・Flowdesk\n・Nextline\n\n語感がやわらかく、読み方に迷わないものを優先する。\nドメインの空き状況もあわせて確認すること。',
      tagIds: ['g4'], createdAt: TS(-8), updatedAt: TS(-1) },
    { id: 'n2', title: '定例MTG 議事録',
      body: '【決定事項】\n・リニューアルの公開は11月末を目標とする\n・デザインは外部に依頼せず社内で進める\n\n【持ち帰り】\n・制作会社2社に見積もりを依頼する\n・現行サイトのアクセス解析を共有する',
      tagIds: ['g1'], createdAt: TS(-3), updatedAt: TS(-3) },
    { id: 'n3', title: '参考リンク集',
      body: 'アクセシビリティのチェック観点\n競合3社のプラン比較表\n社内のデザインガイドライン',
      tagIds: [], createdAt: TS(-20), updatedAt: TS(-15) },
  ];

  // ---- ワークスペース（共有プロジェクト用） ----
  const workspaces = [{ id: WS_ID, name: '営業チーム', ownerId: null, role: 'owner' }];

  // ========================================================================
  const api = {
    _orig: null,
    _guarded: false,

    /** デモデータを注入する（DBへの書き込みは全て封じる） */
    on() {
      if (typeof S === 'undefined') { console.error('Taskra が読み込まれていません'); return; }

      // --- 1) 書き込み・再取得を封じる ---
      if (!this._orig) {
        this._orig = { dbPut: window.dbPut, dbDel: window.dbDel, loadAll: window.loadAll };
      }
      window.dbPut = async () => { console.warn('[demo] dbPut は無効化されています'); };
      window.dbDel = async () => { console.warn('[demo] dbDel は無効化されています'); };
      window.loadAll = async () => { console.warn('[demo] loadAll は無効化されています'); };

      // --- 2) 個人情報を差し替える ---
      // 単に代入するだけでは、Supabase の onAuthStateChange（TOKEN_REFRESHED）が
      // window._currentUser を本物のセッションで上書きし、撮影中に実名とアイコンが
      // 戻ってしまう。setter を挟んで、何が入っても必ず伏せる。
      if (!this._guarded) {
        let _u = window._currentUser;
        const sanitize = (u) => {
          if (!u || typeof u !== 'object') return u;
          try {
            u.email = 'user@example.com';
            u.user_metadata = Object.assign({}, u.user_metadata, {
              full_name: 'Taskra ユーザー',
              name: 'Taskra ユーザー',
              avatar_url: '',
              picture: '',
            });
          } catch (_e) {}
          return u;
        };
        _u = sanitize(_u);
        try { delete window._currentUser; } catch (_e) {}
        Object.defineProperty(window, '_currentUser', {
          configurable: true,
          get() { return _u; },
          set(v) { _u = sanitize(v); },
        });
        this._guarded = true;
      }
      const myId = window._currentUser ? window._currentUser.id : 'demo-user';

      // --- 3) 状態を差し替える ---
      S.projects = JSON.parse(JSON.stringify(projects));
      S.tags     = JSON.parse(JSON.stringify(tags));
      S.notes    = JSON.parse(JSON.stringify(notes));
      S.tasks    = JSON.parse(JSON.stringify(tasks))
                     .map(t => (t.assigneeId === '__ME__' ? { ...t, assigneeId: myId } : t));
      S.workspaces = JSON.parse(JSON.stringify(workspaces));
      // user_name が無いとタスク行の担当者アバターが「?」になる（renderRow が user_name を見る）
      S.wsMembers  = { [WS_ID]: [
        { user_id: myId, user_email: 'user@example.com', user_name: 'Taskra ユーザー', role: 'owner' },
        { user_id: 'demo-member-2', user_email: 'member@example.com', user_name: '佐藤 みなみ', role: 'member' },
      ] };
      S.commentCounts = { t102: 3, t201: 1, t601: 2 };
      S.selectMode = false;
      S.selectedIds = [];
      S.filterTagIds = [];
      S.search = '';
      S.drawerOpen = false;
      S.taskId = null;
      S.noteOpen = false;
      S.noteId = null;

      if (typeof render === 'function') render();
      console.log('%c[demo] デモデータを注入しました。元に戻すには location.reload()', 'color:#10b981;font-weight:bold');
      return 'ok';
    },

    /** ビューを切り替える */
    view(v, opt) {
      S.view = v;
      if (opt && opt.projId) S.projId = opt.projId;
      if (opt && opt.tagId) S.tagId = opt.tagId;
      if (opt && opt.search !== undefined) S.search = opt.search;
      if (typeof render === 'function') render();
      return v;
    },

    /** 元に戻す（実データを読み直す） */
    off() { location.reload(); },
  };

  window.TaskraDemo = api;
  return 'TaskraDemo ready';
})();
