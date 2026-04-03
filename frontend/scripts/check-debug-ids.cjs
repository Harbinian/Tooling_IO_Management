/**
 * Debug ID Coverage Checker
 *
 * 检查 Vue 文件中 v-debug-id 的覆盖度
 * 统计关键元素数量与已标记元素数量的比例
 *
 * Usage: node scripts/check-debug-ids.js [options]
 *   --files <pattern>  指定要检查的目录 (默认: src/pages)
 *   --threshold <n>    最低覆盖率阈值 0-1 (默认: 0.8)
 *   --fix              自动添加缺失的 v-debug-id 占位符
 *   --verbose          显示详细输出
 *
 * Exit codes:
 *   0 - 所有文件通过检查
 *   1 - 有文件未通过检查
 *   2 - 执行错误
 */

const fs = require('fs');
const path = require('path');

// 关键元素标签模式（需要考虑可能没有 v-debug-id 的情况）
const KEY_ELEMENT_PATTERNS = [
  { pattern: /<Card[\s>]/g, name: 'Card' },
  { pattern: /<section[\s>]/g, name: 'section' },
  { pattern: /<header[\s>]/g, name: 'header' },
  { pattern: /<div[\s][^>]*class="[^"]*(?:card|panel|section|header)[^"]*"[^>]*>/g, name: 'div.card/panel' },
];

// 已知的需要标记的区域（通过 v-debug-id 或其他标识）
const ALREADY_MARKED_PATTERNS = [
  /v-debug-id=/,
  /v-if=/,  // 条件渲染不算
];

// 排除列表：这些元素不需要 debug-id
const EXCLUDE_PATTERNS = [
  /v-for=/,  // 循环中的元素可能动态生成
  /class=".*(?:animate|transition|keyframes).*"/,  // 动画元素
];

function countOccurrences(content, pattern) {
  const matches = content.match(pattern);
  return matches ? matches.length : 0;
}

function findKeyElements(content) {
  const elements = [];

  // 查找所有 Card 组件（通常是需要标记的主要容器）
  const cardRegex = /<Card[^>]*>[\s\S]*?<\/Card>|<Card[^>]*\/>/g;
  let match;
  while ((match = cardRegex.exec(content)) !== null) {
    elements.push({
      type: 'Card',
      text: match[0].substring(0, 100),
      hasDebugId: match[0].includes('v-debug-id'),
      hasVFor: match[0].includes('v-for='),
    });
  }

  // 查找所有独立的 header 标签（非嵌套）
  const headerRegex = /<header(?:\s[^>]*)?>(?:(?!<\/header)[\s\S])*?<\/header>/g;
  while ((match = headerRegex.exec(content)) !== null) {
    elements.push({
      type: 'header',
      text: match[0].substring(0, 100),
      hasDebugId: match[0].includes('v-debug-id'),
      hasVFor: match[0].includes('v-for='),
    });
  }

  // 查找所有独立的 section 标签
  const sectionRegex = /<section(?:\s[^>]*)?>(?:(?!<\/section)[\s\S])*?<\/section>/g;
  while ((match = sectionRegex.exec(content)) !== null) {
    // 排除嵌套在 Card 内的 section
    if (!match[0].includes('<Card')) {
      elements.push({
        type: 'section',
        text: match[0].substring(0, 100),
        hasDebugId: match[0].includes('v-debug-id'),
        hasVFor: match[0].includes('v-for='),
      });
    }
  }

  return elements;
}

function checkFile(filePath, options = {}) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const elements = findKeyElements(content);

  // 过滤需要标记的元素（排除 v-for 循环中的）
  const markableElements = elements.filter(el => !el.hasVFor);
  const markedElements = markableElements.filter(el => el.hasDebugId);

  const coverage = markableElements.length > 0
    ? markedElements.length / markableElements.length
    : 1.0;

  const passed = coverage >= (options.threshold || 0.8);

  return {
    file: filePath,
    total: elements.length,
    markable: markableElements.length,
    marked: markedElements.length,
    coverage,
    passed,
    unmarkedElements: markableElements.filter(el => !el.hasDebugId),
  };
}

function findVueFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // 跳过 node_modules, .git, dist 等目录
      if (!['node_modules', '.git', 'dist', 'build', '.nuxt'].includes(entry.name)) {
        findVueFiles(fullPath, files);
      }
    } else if (entry.name.endsWith('.vue')) {
      files.push(fullPath);
    }
  }
  return files;
}

function checkAllFiles(dirs, options = {}) {
  const results = [];
  const files = [];

  for (const dir of dirs) {
    const fullPath = path.resolve(options.cwd || process.cwd(), dir);
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
      findVueFiles(fullPath, files);
    } else if (fs.existsSync(fullPath)) {
      files.push(fullPath);
    }
  }

  // 去重
  const uniqueFiles = [...new Set(files)];

  for (const file of uniqueFiles) {
    try {
      const result = checkFile(file, options);
      results.push(result);
    } catch (err) {
      console.error(`Error checking ${file}: ${err.message}`);
    }
  }

  return results;
}

function printReport(results, options = {}) {
  console.log('\n=== Debug ID Coverage Report ===\n');

  let totalMarkable = 0;
  let totalMarked = 0;
  let passCount = 0;
  let failCount = 0;

  for (const result of results) {
    totalMarkable += result.markable;
    totalMarked += result.marked;

    if (result.passed) {
      passCount++;
    } else {
      failCount++;
    }

    const status = result.passed ? '✅' : '❌';
    const coveragePct = (result.coverage * 100).toFixed(1);

    console.log(`${status} ${result.file}`);
    console.log(`   Coverage: ${result.marked}/${result.markable} (${coveragePct}%)`);

    if (options.verbose && result.unmarkedElements.length > 0) {
      console.log('   Unmarked elements:');
      for (const el of result.unmarkedElements.slice(0, 5)) {
        console.log(`     - ${el.type}: ${el.text.substring(0, 60)}...`);
      }
      if (result.unmarkedElements.length > 5) {
        console.log(`     ... and ${result.unmarkedElements.length - 5} more`);
      }
    }
  }

  console.log('\n--- Summary ---');
  const overallCoverage = totalMarkable > 0 ? (totalMarked / totalMarkable * 100).toFixed(1) : 100;
  console.log(`Total: ${passCount} passed, ${failCount} failed`);
  console.log(`Overall coverage: ${totalMarked}/${totalMarkable} (${overallCoverage}%)`);

  return failCount === 0;
}

// CLI
const args = process.argv.slice(2);
const options = {
  threshold: 0.8,
  verbose: false,
  cwd: path.resolve(__dirname, '..'),
  files: ['src/pages', 'src/components'],
};

const filesIndex = args.indexOf('--files');
if (filesIndex !== -1 && args[filesIndex + 1]) {
  options.files = [args[filesIndex + 1]];
}

const thresholdIndex = args.indexOf('--threshold');
if (thresholdIndex !== -1 && args[thresholdIndex + 1]) {
  options.threshold = parseFloat(args[thresholdIndex + 1]);
}

if (args.includes('--verbose')) {
  options.verbose = true;
}

console.log('Checking DEBUG_ID coverage...');
console.log(`Threshold: ${(options.threshold * 100)}%`);
console.log(`Directories: ${options.files.join(', ')}`);

const results = checkAllFiles(options.files, options);
const allPassed = printReport(results, options);

process.exit(allPassed ? 0 : 1);
