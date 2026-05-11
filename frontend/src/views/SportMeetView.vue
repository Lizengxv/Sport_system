<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <h2>运动会管理</h2>
      <div class="nav-group">
        <button class="nav-item" :class="{ active: active === 'home' }" @click="active = 'home'">系统首页</button>
        <button class="nav-item" :class="{ active: active === 'athletes' }" @click="active = 'athletes'">运动员管理</button>
        <button class="nav-item" :class="{ active: active === 'events' }" @click="active = 'events'">项目管理</button>
        <button class="nav-item" :class="{ active: active === 'results' || active === 'results-query' }" @click="toggleResultsMenu">成绩管理</button>
        <div v-if="resultsMenuOpen" class="nav-submenu">
          <button class="nav-sub-item" :class="{ active: active === 'results' }" @click="openResultsEntry">成绩录入</button>
          <button class="nav-sub-item" :class="{ active: active === 'results-query' }" @click="openResultsQuery">成绩查询</button>
        </div>
        <button class="nav-item" :class="{ active: active === 'groups' }" @click="active = 'groups'">分组管理</button>
        <button class="nav-item" :class="{ active: active === 'ranking' }" @click="active = 'ranking'">排名管理</button>
      </div>
    </aside>

    <main class="content-area">
      <section v-if="active === 'home'">
        <h3>田径运动会管理系统</h3>
        <p class="muted">请选择左侧模块开始操作</p>
      </section>

      <section v-else-if="active === 'athletes'">
        <div class="panel-header">
          <h3>运动员管理</h3>
          <div class="toolbar">
            <input type="file" ref="athleteFile" @change="importAthletes" />
            <button class="btn secondary" @click="openCreateModal">新增</button>
            <button class="btn secondary" @click="downloadTemplate">导出模板</button>
            <button class="btn secondary" @click="exportAthletes">导出</button>
            <button class="btn secondary" @click="fetchAthletes">刷新</button>
          </div>
        </div>
        <p v-if="importMessage" class="muted">{{ importMessage }}</p>

        <div class="form-row"><label>学号</label><input v-model="athleteQuery.student_id" placeholder="输入学号" /></div>
        <div class="form-row"><label>姓名</label><input v-model="athleteQuery.name" placeholder="输入姓名" /></div>
        <button class="btn secondary" @click="searchAthletes">查询</button>

        <table class="table" style="margin-top: 12px">
          <thead>
            <tr>
              <th>学院</th>
              <th>姓名</th>
              <th>学号</th>
              <th>性别</th>
              <th>项目</th>
              <th>组别</th>
              <th>成绩</th>
              <th>排名</th>
              <th>积分</th>
              <th>破纪录</th>
              <th>电话</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in athletes" :key="row.id">
              <td>{{ row.college }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.student_id }}</td>
              <td>{{ row.gender }}</td>
              <td>{{ row.event }}</td>
              <td>{{ displayGroupName(row.group_name) }}</td>
              <td>{{ row.score ?? '' }}</td>
              <td>{{ row.rank ?? '' }}</td>
              <td>{{ row.points ?? '' }}</td>
              <td>{{ row.record_broken ? '是' : '否' }}</td>
              <td>{{ row.phone ?? '' }}</td>
              <td>
                <button class="btn secondary" @click="openEditModal(row)">编辑</button>
                <button class="btn secondary" @click="deleteAthlete(row.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="showModal" class="modal-backdrop">
          <div class="modal">
            <div class="panel-header">
              <h3>{{ modalMode === 'create' ? '新增运动员' : '编辑运动员' }}</h3>
              <button class="btn secondary" @click="closeModal">关闭</button>
            </div>
            <div class="modal-body">
              <div class="form-row"><label>学院</label><input v-model="modalForm.college" /></div>
              <div class="form-row"><label>姓名</label><input v-model="modalForm.name" /></div>
              <div class="form-row"><label>学号</label><input v-model="modalForm.student_id" /></div>
              <div class="form-row"><label>性别</label><input v-model="modalForm.gender" /></div>
              <div class="form-row"><label>项目</label><input v-model="modalForm.event" /></div>
              <div class="form-row"><label>电话</label><input v-model="modalForm.phone" /></div>
            </div>
            <div class="toolbar">
              <button class="btn" @click="submitModal">保存</button>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="active === 'events'">
        <div class="panel-header">
          <h3>项目管理</h3>
          <div class="toolbar">
            <button class="btn secondary" :class="{ active: eventsRefreshActive }" @click="initEvents">刷新项目</button>
            <button class="btn secondary" @click="exportEvents">导出</button>
          </div>
        </div>
        <p v-if="eventsRefreshMessage" class="muted">{{ eventsRefreshMessage }}</p>

        <table class="table">
          <thead>
            <tr>
              <th>项目</th>
              <th>人数</th>
              <th>最好成绩</th>
              <th>保持者</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in events" :key="row.id">
              <td>{{ row.name }}</td>
              <td>{{ row.participant_count }}</td>
              <td>{{ row.best_record ?? '暂无' }}</td>
              <td>{{ row.record_holder || '暂无' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-else-if="active === 'groups'">
        <div class="panel-header">
          <h3>分组管理</h3>
          <div class="toolbar">
            <button class="btn secondary" @click="exportGroupsTemplate">导出模板</button>
            <button class="btn secondary" @click="confirmGroups">保存分组</button>
            <button class="btn secondary" @click="exportGroups">导出</button>
          </div>
        </div>
        <p v-if="groupMessage" class="muted">{{ groupMessage }}</p>

        <div class="form-row">
          <label>项目</label>
          <select v-model="groupForm.event">
            <option value="">请选择项目</option>
            <option v-for="item in eventOptions" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>性别</label>
          <select v-model="groupForm.gender">
            <option value="">请选择性别</option>
            <option value="男">男</option>
            <option value="女">女</option>
            <option value="混合">混合</option>
          </select>
        </div>
        <div class="form-row">
          <label>轮次</label>
          <select v-model="groupForm.round">
            <option value="prelim">预赛</option>
            <option value="semi">半决赛</option>
            <option value="final">决赛</option>
            <option value="one">一轮次</option>
          </select>
        </div>
        <div class="form-row">
          <label>每组人数</label>
          <select v-model="groupForm.per_group">
            <option value="">请选择</option>
            <option :value="4">4</option>
            <option :value="5">5</option>
            <option :value="6">6</option>
            <option :value="7">7</option>
            <option :value="8">8</option>
          </select>
        </div>
        <div class="form-row">
          <label>组数</label>
          <select v-model="groupForm.group_count">
            <option value="">请选择</option>
            <option :value="1">1</option>
            <option :value="2">2</option>
            <option :value="3">3</option>
            <option :value="4">4</option>
            <option :value="5">5</option>
          </select>
        </div>

        <div class="toolbar">
          <button class="btn secondary" @click="queryGroupCandidates">查询人员</button>
          <button class="btn" @click="generateGroups">生成分组</button>
        </div>

        <div class="split-panel">
          <div class="panel-card">
            <h4>未分组人员（{{ ungrouped.length }}人）</h4>
            <table class="table">
              <thead><tr><th>学院</th><th>姓名</th><th>{{ identityColumnLabel(groupForm.event, ungrouped) }}</th></tr></thead>
              <tbody>
                <tr v-for="row in ungrouped" :key="row.id"><td>{{ row.college }}</td><td>{{ row.name }}</td><td>{{ row.student_id }}</td></tr>
              </tbody>
            </table>
          </div>

          <div class="panel-arrows"><div class="arrow">→</div><div class="arrow">→</div></div>

          <div class="panel-card">
            <h4>已分组人员</h4>
            <table class="table">
              <thead><tr><th>学院</th><th>姓名</th><th>{{ identityColumnLabel(selectedGroupEvent || groupForm.event, selectedGroupRows) }}</th><th>组别</th><th>{{ usesBibNumber(selectedGroupEvent || groupForm.event) ? '号码' : '道次' }}</th></tr></thead>
              <tbody>
                <tr v-for="(row, idx) in selectedGroupRows" :key="idx">
                  <td>{{ row.college }}</td><td>{{ row.name }}</td><td>{{ row.student_id }}</td>
                  <td><input v-model="row.group_label" /></td><td><input v-model.number="row.lane" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="panel-header" style="margin-top: 24px">
          <h4>分组结果</h4>
          <div class="toolbar">
            <button class="btn secondary" @click="queryGroups">查询分组</button>
            <select v-model="groupQuery.event" style="min-width: 140px">
              <option value="">请选择项目</option>
              <option v-for="item in eventOptions" :key="`q-${item}`" :value="item">{{ item }}</option>
            </select>
            <select v-model="groupQuery.gender" style="min-width: 120px">
              <option value="">请选择性别</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="混合">混合</option>
            </select>
            <select v-model="groupQuery.round" style="min-width: 140px">
              <option value="">请选择轮次</option>
              <option value="prelim">预赛</option>
              <option value="semi">半决赛</option>
              <option value="final">决赛</option>
              <option value="one">一轮次</option>
            </select>
          </div>
        </div>

        <div v-if="groupedResults.length === 0" class="muted">暂无分组结果</div>
        <h4 v-if="groupedResults.length" style="margin-top: 8px">{{ groupRoundText }}</h4>
        <div v-for="(group, idx) in groupedResults" :key="`${group.event}-${group.label}-${idx}`" style="margin-top: 12px">
          <h4><button class="btn secondary" @click="selectGroup(group.event, group.label)">{{ formatGroupResultTitle(group) }}</button></h4>
          <table class="table">
            <thead><tr><th>项目</th><th>学院</th><th>{{ identityColumnLabel(group.event, group.rows) }}</th><th>姓名</th><th>组别</th><th>{{ usesBibNumber(group.event) ? '号码' : '道次' }}</th></tr></thead>
            <tbody>
              <tr v-for="(row, rowIdx) in group.rows" :key="rowIdx">
                <td>{{ row.event }}</td><td>{{ row.college }}</td><td>{{ row.student_id }}</td><td>{{ row.name }}</td>
                <td><input v-model="row.group_label" /></td><td><input v-model.number="row.lane" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="active === 'results'">
        <div class="panel-header">
          <h3>成绩录入</h3>
          <div class="toolbar">
            <button class="btn secondary" @click="fetchEventOptions">刷新项目</button>
            <button class="btn secondary" @click="exportResults">导出</button>
          </div>
        </div>

        <div class="form-row">
          <label>项目</label>
          <select v-model="resultForm.event">
            <option value="">请选择项目</option>
            <option v-for="item in eventOptions" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>性别</label>
          <select v-model="resultForm.gender">
            <option value="">请选择性别</option>
            <option value="男">男</option>
            <option value="女">女</option>
            <option value="混合">混合</option>
          </select>
        </div>
        <div class="form-row">
          <label>轮次</label>
          <select v-model="resultForm.round">
            <option value="prelim">预赛</option>
            <option value="semi">半决赛</option>
            <option value="final">决赛</option>
            <option value="one">一轮次</option>
          </select>
        </div>
        <div class="form-row">
          <label>成绩单位</label>
          <select v-model="resultForm.unit">
            <option value="秒">秒</option>
            <option value="毫秒">毫秒</option>
            <option value="厘米">厘米</option>
            <option value="米">米</option>
          </select>
        </div>
        <button class="btn secondary" @click="queryRoster">查询名单</button>
        <button class="btn" @click="submitBatchResults">保存成绩</button>
        <p v-if="resultMessage" class="muted">{{ resultMessage }}</p>

                <div v-if="!resultsRosterGroups.length" class="muted" style="margin-top: 16px">暂无录入名单</div>
        <div v-else>
          <div v-for="group in resultsRosterGroups" :key="`entry-${group.label || 'ungrouped'}`" style="margin-top: 16px">
            <h4 style="margin-bottom: 8px">{{ group.displayLabel }}</h4>
            <table class="table">
              <thead>
                <tr>
                  <th>项目</th><th>学院</th><th>姓名</th><th>{{ identityColumnLabel(resultForm.event, group.rows) }}</th><th>{{ usesBibNumber(resultForm.event) ? '号码' : '道次' }}</th><th>成绩</th><th>排名</th><th>日期</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in group.rows" :key="`${group.label || 'ungrouped'}-${row.id}-${row.student_id}`">
                  <td>{{ resultForm.event }}</td>
                  <td>{{ row.college }}</td>
                  <td>{{ row.name }}</td>
                  <td>{{ row.student_id }}</td>
                  <td>{{ row.lane ?? '' }}</td>
                  <td>
                    <div v-if="isDistanceEvent(resultForm.event)" class="distance-score">
                      <div class="distance-row">
                        <input v-model.number="row.attempt1" placeholder="第一次" />
                        <input v-model.number="row.attempt2" placeholder="第二次" />
                        <input v-model.number="row.attempt3" placeholder="第三次" />
                      </div>
                      <div class="muted">最佳：{{ bestAttempt(row) || '' }}</div>
                    </div>
                    <div v-else class="score-input">
                      <input v-model.number="row.inputScore" />
                      <span class="unit-badge">{{ resultForm.unit }}</span>
                    </div>
                  </td>
                  <td>{{ row.rank ?? '' }}</td>
                  <td>{{ row.date ? formatDate(row.date) : '' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section v-else-if="active === 'results-query'">
        <div class="panel-header">
          <h3>成绩查询</h3>
          <div class="toolbar">
            <button class="btn secondary" @click="searchResults">查询</button>
            <button class="btn secondary" @click="exportResults">导出</button>
            <button class="btn secondary" @click="exportResultsTemplate">导出模板</button>
          </div>
        </div>

        <div class="form-row"><label>项目</label><select v-model="resultsQuery.event"><option value="">请选择项目</option><option v-for="item in eventOptions" :key="`rq-${item}`" :value="item">{{ item }}</option></select></div>
        <div class="form-row">
          <label>性别</label>
          <select v-model="resultsQuery.gender">
            <option value="">请选择性别</option>
            <option value="男">男</option>
            <option value="女">女</option>
            <option value="混合">混合</option>
          </select>
        </div>
        <div class="form-row"><label>学院</label><input v-model="resultsQuery.college" placeholder="输入学院" /></div>
        <div class="form-row"><label>姓名</label><input v-model="resultsQuery.name" placeholder="输入姓名" /></div>
        <div class="form-row"><label>学号</label><input v-model="resultsQuery.student_id" placeholder="输入学号" /></div>
        <div class="form-row">
          <label>轮次</label>
          <select v-model="resultsQuery.round">
            <option value="">全部轮次</option>
            <option value="prelim">预赛</option>
            <option value="semi">半决赛</option>
            <option value="final">决赛</option>
            <option value="one">一轮次</option>
          </select>
        </div>

        <div v-if="!resultsTable.length" class="muted" style="margin-top: 12px">暂无查询结果</div>
        <div v-else-if="!resultsQuery.round" style="margin-top: 12px">
          <div v-for="group in queryRoundGroups" :key="`round-${group.round}`" style="margin-top: 12px">
            <h4 style="margin-bottom: 8px">{{ group.label }}</h4>
            <table class="table">
              <thead>
                <tr>
                  <th>项目</th><th>姓名</th><th>学号</th><th>学院</th><th>成绩</th><th>排名</th><th>轮次</th><th>破纪录</th><th>日期</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in group.rows" :key="`${group.round}-${row.id}-${row.student_id}`">
                  <td>{{ row.event }}</td>
                  <td>{{ row.name }}</td>
                  <td>{{ row.student_id }}</td>
                  <td>{{ row.college }}</td>
                  <td>{{ row.score }}</td>
                  <td>{{ row.rank }}</td>
                  <td>{{ row.round }}</td>
                  <td>{{ row.record_broken ? '是' : '否' }}</td>
                  <td>{{ formatDate(row.date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <table v-else class="table" style="margin-top: 12px">
          <thead>
            <tr>
              <th>项目</th><th>姓名</th><th>学号</th><th>学院</th><th>成绩</th><th>排名</th><th>轮次</th><th>破纪录</th><th>日期</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in resultsTable" :key="row.id">
              <td>{{ row.event }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.student_id }}</td>
              <td>{{ row.college }}</td>
              <td>{{ row.score }}</td>
              <td>{{ row.rank }}</td>
              <td>{{ row.round }}</td>
              <td>{{ row.record_broken ? '是' : '否' }}</td>
              <td>{{ formatDate(row.date) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-else>
        <div class="panel-header">
          <h3>排名</h3>
          <div class="toolbar">
            <button class="btn secondary" @click="initPersonalRanking">初始化个人排名</button>
            <button class="btn secondary" @click="initCollegeRanking">初始化学院排名</button>
            <button class="btn secondary" @click="exportPersonalRanking">导出个人排名</button>
            <button class="btn secondary" @click="exportCollegeRanking">导出学院排名</button>
          </div>
        </div>

        <h4>个人排名</h4>
        <table class="table">
          <thead>
            <tr><th>学号</th><th>姓名</th><th>学院</th><th>项目</th><th>成绩</th><th>排名</th><th>积分</th><th>总积分</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in personalRankings" :key="row.id">
              <td>{{ row.student_id }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.college }}</td>
              <td>{{ row.event }}</td>
              <td>{{ row.score }}</td>
              <td>{{ row.rank }}</td>
              <td>{{ row.points }}</td>
              <td>{{ row.total_points }}</td>
            </tr>
          </tbody>
        </table>

        <h4 style="margin-top: 24px">学院排名</h4>
        <table class="table">
          <thead>
            <tr><th>学院</th><th>项目数量</th><th>参赛人数</th><th>总积分</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in collegeRankings" :key="row.id">
              <td>{{ row.college }}</td>
              <td>{{ row.event_count }}</td>
              <td>{{ row.participant_count }}</td>
              <td>{{ row.total_points }}</td>
            </tr>
          </tbody>
        </table>

        <h4 style="margin-top: 24px">团体积分</h4>

        <h5 style="margin-top: 16px">男子团体</h5>
        <table class="table">
          <thead>
            <tr><th>项目</th><th>学院</th><th>成绩</th><th>排名</th><th>积分</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in teamRankings.male" :key="`male-${row.event}-${row.student_id}-${row.rank}`">
              <td>{{ row.event }}</td>
              <td>{{ row.college }}</td>
              <td>{{ row.score }}</td>
              <td>{{ row.rank }}</td>
              <td>{{ row.points }}</td>
            </tr>
          </tbody>
        </table>

        <h5 style="margin-top: 16px">女子团体</h5>
        <table class="table">
          <thead>
            <tr><th>项目</th><th>学院</th><th>成绩</th><th>排名</th><th>积分</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in teamRankings.female" :key="`female-${row.event}-${row.student_id}-${row.rank}`">
              <td>{{ row.event }}</td>
              <td>{{ row.college }}</td>
              <td>{{ row.score }}</td>
              <td>{{ row.rank }}</td>
              <td>{{ row.points }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<script setup>
  import { computed, onMounted, reactive, ref, watch } from 'vue';
import api from '../api';

const active = ref('home');
const resultsMenuOpen = ref(false);
const athletes = ref([]);
const events = ref([]);
const groups = ref([]);
const results = ref([]);
const personalRankings = ref([]);
const collegeRankings = ref([]);
const teamRankings = ref({ male: [], female: [] });
const athleteFile = ref(null);
const eventOptions = ref([]);
const roster = ref([]);
const resultMessage = ref('');
const importMessage = ref('');
const eventsRefreshMessage = ref('');
const eventsRefreshActive = ref(false);
const groupMessage = ref('');
const getRoundLabel = (round) => {
  if (round === 'prelim') return '预赛';
  if (round === 'semi') return '半决赛';
  if (round === 'final') return '决赛';
  if (round === 'one') return '一轮次';
  return '';
};

const groupRoundText = computed(() => {
  const round = groupQuery.round || groupForm.round;
  return getRoundLabel(round);
});

const showModal = ref(false);
const modalMode = ref('create');
const modalForm = reactive({
  id: null,
  college: '',
  name: '',
  student_id: '',
  gender: '',
  event: '',
  phone: '',
});

const athleteQuery = reactive({ student_id: '', name: '' });

const groupForm = reactive({
  event: '',
  gender: '',
  round: 'prelim',
  per_group: '',
  group_count: '',
});
const groupQuery = reactive({
  event: '',
  gender: '',
  round: '',
});
watch(
  () => groupForm.per_group,
  (value) => {
    if (value !== '' && groupForm.group_count !== '') {
      groupForm.group_count = '';
    }
  },
);
watch(
  () => groupForm.group_count,
  (value) => {
    if (value !== '' && groupForm.per_group !== '') {
      groupForm.per_group = '';
    }
  },
);
const ungrouped = ref([]);
const groupedResults = ref([]);
const selectedGroupLabel = ref('');
const selectedGroup = computed(() => {
  if (!selectedGroupLabel.value) return null;
  const [event, label] = selectedGroupLabel.value.split('__');
  return groupedResults.value.find((item) => item.event === event && item.label === label) || null;
});
const selectedGroupRows = computed(() => (selectedGroup.value ? selectedGroup.value.rows : []));
const selectedGroupEvent = computed(() => selectedGroup.value?.event || groupQuery.event || groupForm.event || '');


const isLongDistanceEvent = (eventName) => {
  if (!eventName) return false;
  const value = String(eventName).trim();
  if (!value) return false;
  const match = value.match(/(\d+)/);
  if (!match) return false;
  const meters = Number(match[1]);
  return Number.isFinite(meters) && meters >= 800;
};

const usesBibNumber = (eventName) => isLongDistanceEvent(eventName) || isDistanceEvent(eventName) || isHighJumpEvent(eventName);

const isRelayEvent = (eventName) => ['4*100', '4?100', '4x100', '4*200', '4?200', '4x200', '4*400', '4?400', '4x400', '接力', 'relay'].some((keyword) => normalizeEventName(eventName).includes(String(keyword).toLowerCase()));

const rowsUseTeamCode = (rows) => Array.isArray(rows) && rows.some((row) => String(row?.student_id || '').startsWith('TEAM_'));

const identityColumnLabel = (eventName, rows = []) => ((rowsUseTeamCode(rows) || isRelayEvent(eventName)) ? '队伍编号' : '学号');

const CHINESE_GROUP_DIGITS = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];

const toChineseGroupNumber = (value) => {
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) return '';
  if (number < 10) return CHINESE_GROUP_DIGITS[number];
  if (number === 10) return '十';
  if (number < 20) return `十${CHINESE_GROUP_DIGITS[number % 10]}`;
  if (number < 100) {
    const tens = Math.floor(number / 10);
    const ones = number % 10;
    return `${CHINESE_GROUP_DIGITS[tens]}十${ones ? CHINESE_GROUP_DIGITS[ones] : ''}`;
  }
  return String(number);
};

const groupLabelOrderValue = (label) => {
  if (!label) return 999;
  const text = String(label).trim().replace(/组$/, '');
  if (!text) return 999;
  if (/^\d+$/.test(text)) return Number(text);
  if (/^[A-Z]$/i.test(text)) return text.toUpperCase().charCodeAt(0) - 'A'.charCodeAt(0) + 1;
  const tenIndex = text.indexOf('十');
  if (tenIndex !== -1) {
    const left = text.slice(0, tenIndex);
    const right = text.slice(tenIndex + 1);
    const tens = left ? CHINESE_GROUP_DIGITS.indexOf(left) : 1;
    const ones = right ? CHINESE_GROUP_DIGITS.indexOf(right) : 0;
    if (tens >= 0 && ones >= 0) return tens * 10 + ones;
  }
  const digitIndex = CHINESE_GROUP_DIGITS.indexOf(text);
  if (digitIndex >= 0) return digitIndex;
  return 999;
};

const normalizeGroupLabel = (value) => {
  if (!value) return '';
  const text = String(value).trim().replace(/组$/, '');
  if (!text) return '';
  if (/^[A-Z]$/i.test(text)) {
    return toChineseGroupNumber(text.toUpperCase().charCodeAt(0) - 'A'.charCodeAt(0) + 1);
  }
  if (/^\d+$/.test(text)) {
    return toChineseGroupNumber(Number(text));
  }
  return text;
};

const groupGenderText = (gender) => {
  if (gender === '') return '';
  if (gender === '') return '';
  if (gender === '') return '';
  return '';
};

const formatGroupResultTitle = (group) => {
  const roundText = getRoundLabel(groupQuery.round || groupForm.round);
  const groupText = group?.label ? `${normalizeGroupLabel(group.label)}组` : '';
  return [roundText, group?.event || '', groupText].filter(Boolean).join('-');
};

const formatRosterGroupLabel = (label) => {
  if (!label) return '未分组';
  const text = normalizeGroupLabel(label);
  return text.endsWith('组') ? text : `${text}组`;
};

const resultsRosterGroups = computed(() => {
  const bucket = new Map();
  for (const row of roster.value || []) {
    const key = String(row?.group_label || '');
    if (!bucket.has(key)) {
      bucket.set(key, []);
    }
    bucket.get(key).push(row);
  }

  return Array.from(bucket.entries())
    .sort((a, b) => {
      const labelA = String(a[0] || '');
      const labelB = String(b[0] || '');
      if (!labelA && labelB) return 1;
      if (labelA && !labelB) return -1;
      const orderDiff = groupLabelOrderValue(labelA) - groupLabelOrderValue(labelB);
      if (orderDiff !== 0) return orderDiff;
      return labelA.localeCompare(labelB, undefined, { numeric: true });
    })
    .map(([label, rows]) => ({
      label,
      displayLabel: formatRosterGroupLabel(label),
      rows,
    }));
});

const toggleResultsMenu = () => {
  resultsMenuOpen.value = !resultsMenuOpen.value;
  active.value = 'results';
};

const openResultsEntry = () => {
  resultsMenuOpen.value = true;
  active.value = 'results';
};

const openResultsQuery = () => {
  resultsMenuOpen.value = true;
  active.value = 'results-query';
};

const resultForm = reactive({ event: '', gender: '', round: 'final', unit: '秒' });
const resultsQuery = reactive({ event: '', gender: '', college: '', name: '', student_id: '', round: '' });


const normalizeEventName = (eventName) => {
  if (!eventName) return '';
  return String(eventName).trim().toLowerCase().replace(/\s+/g, '');
};

const isHighJumpEvent = (eventName) => {
  const value = normalizeEventName(eventName);
  return value.includes('\u8df3\u9ad8') || value.includes('highjump') || value.includes('high-jump');
};

const isDistanceEvent = (eventName) => {
  const value = normalizeEventName(eventName);
  if (!value || isHighJumpEvent(value)) return false;
  const keywords = [
    '\u8df3\u8fdc',
    '\u4e09\u7ea7\u8df3\u8fdc',
    '\u7acb\u5b9a\u8df3\u8fdc',
    '\u6025\u884c\u8df3\u8fdc',
    '\u94c5\u7403',
    '\u6807\u67aa',
    '\u94c1\u997c',
    'longjump',
    'triplejump',
    'shotput',
    'javelin',
    'discus',
  ];
  return keywords.some((k) => value.includes(String(k).toLowerCase()));
};

const supportsGroupCountMode = (eventName) => isHighJumpEvent(eventName) || isDistanceEvent(eventName) || isLongDistanceEvent(eventName);

const displayGroupName = (value) => {
  if (!value) return '';
  const textValue = String(value);
  const mojibakeChars = /[???????????????????????????????????????????????????????]/g;
  const hits = (textValue.match(mojibakeChars) || []).length;
  if (hits < 2) return textValue.replace(/([A-Z])组/g, (_, letter) => `${normalizeGroupLabel(letter)}组`);
  const label = textValue.match(/[A-Z]/)?.[0] || '';
  return label ? `${normalizeGroupLabel(label)}组` : '';
};

const bestAttempt = (row) => {
  const vals = [row.attempt1, row.attempt2, row.attempt3].filter((v) => v !== null && v !== undefined && v !== '');
  if (!vals.length) return '';
  return Math.max(...vals);
};

const fetchAthletes = async () => {
  const { data } = await api.get('/athletes');
  athletes.value = data || [];
};

const searchAthletes = async () => {
  const params = {};
  if (athleteQuery.student_id) params.student_id = athleteQuery.student_id;
  if (athleteQuery.name) params.name = athleteQuery.name;
  const { data } = await api.get('/athletes', { params }).catch(() => ({ data: [] }));
  athletes.value = data || [];
};

const importAthletes = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);
  importMessage.value = '';

  try {
    const { data } = await api.post('/athletes/import', formData);
    importMessage.value = data?.message || 'Import success';
    await fetchAthletes();
    await fetchEventOptions();
  } catch (error) {
    const detail = error?.response?.data?.detail;
    importMessage.value = detail || 'Import failed. Please check template headers and values.';
    window.alert(importMessage.value);
  }

  if (athleteFile.value) athleteFile.value.value = '';
};

const downloadTemplate = () => window.open(`${api.defaults.baseURL}/athletes/template`, '_blank');
const exportAthletes = () => window.open(`${api.defaults.baseURL}/athletes/export`, '_blank');

const openCreateModal = () => {
  modalMode.value = 'create';
  Object.assign(modalForm, { id: null, college: '', name: '', student_id: '', gender: '', event: '', phone: '' });
  showModal.value = true;
};

const openEditModal = (row) => {
  modalMode.value = 'edit';
  Object.assign(modalForm, {
    id: row.id,
    college: row.college,
    name: row.name,
    student_id: row.student_id,
    gender: row.gender,
    event: row.event,
    phone: row.phone || '',
  });
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const submitModal = async () => {
  if (!modalForm.college || !modalForm.name || !modalForm.student_id || !modalForm.gender || !modalForm.event) return;
  const payload = {
    college: modalForm.college,
    name: modalForm.name,
    student_id: modalForm.student_id,
    gender: modalForm.gender,
    event: modalForm.event,
    phone: modalForm.phone,
  };
  if (modalMode.value === 'create') await api.post('/athletes', payload);
  else await api.put(`/athletes/${modalForm.id}`, payload);
  showModal.value = false;
  await fetchAthletes();
};

const deleteAthlete = async (id) => {
  await api.delete(`/athletes/${id}`);
  await fetchAthletes();
};

const initEvents = async () => {
  eventsRefreshMessage.value = '';
  eventsRefreshActive.value = true;
  await fetchEvents();
  eventsRefreshMessage.value = '';
  window.alert(eventsRefreshMessage.value);
  setTimeout(() => {
    eventsRefreshActive.value = false;
  }, 800);
};

const fetchEvents = async () => {
  const { data } = await api.get('/events/list').catch(() => ({ data: [] }));
  events.value = data || [];
};

const exportEvents = () => window.open(`${api.defaults.baseURL}/export/events`, '_blank');

const loadGroupResultsByRows = (rows, append = false, genderHint = '') => {
  const byKey = new Map();
  for (const item of rows || []) {
    const groupLabel = normalizeGroupLabel(item.group_label);
    const normalizedItem = { ...item, group_label: groupLabel };
    const key = `${normalizedItem.event || ''}__${groupLabel}`;
    if (!byKey.has(key)) {
      byKey.set(key, { event: normalizedItem.event || '', label: groupLabel, gender: genderHint, rows: [] });
    }
    byKey.get(key).rows.push(normalizedItem);
  }
  const grouped = Array.from(byKey.values());
  grouped.sort((a, b) => {
    if (a.event === b.event) {
      const orderDiff = groupLabelOrderValue(a.label) - groupLabelOrderValue(b.label);
      if (orderDiff !== 0) return orderDiff;
      return a.label.localeCompare(b.label);
    }
    return a.event.localeCompare(b.event);
  });
  groupedResults.value = append ? [...groupedResults.value, ...grouped.map((g) => ({ ...g, gender: g.gender || genderHint }))] : grouped;
  groups.value = [];
  selectedGroupLabel.value = '';
};

const shuffleArray = (items) => {
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

const buildGroupLaneValues = (eventName, count) => {
  if (usesBibNumber(eventName)) {
    const upperBound = Math.max(30, count);
    return shuffleArray(Array.from({ length: upperBound }, (_, i) => i + 1)).slice(0, count);
  }
  return shuffleArray(Array.from({ length: count }, (_, i) => i + 1));
};

const buildGroupedRows = (picked, label) => {
  const lanes = buildGroupLaneValues(groupForm.event, picked.length);
  return picked.map((row, idx) => ({
    ...row,
    event: groupForm.event || row.event,
    group_label: label,
    lane: lanes[idx],
  }));
};

const generateGroups = async () => {
  if (!ungrouped.value.length) return;
  groupMessage.value = '';
  const perGroup = Number(groupForm.per_group) || 0;
  const groupCount = Number(groupForm.group_count) || 0;

  if (!perGroup && !groupCount) {
    groupMessage.value = '请选择每组人数或组数';
    window.alert(groupMessage.value);
    return;
  }

  if (perGroup && groupCount) {
    groupMessage.value = '每组人数和组数只能选择一种';
    window.alert(groupMessage.value);
    return;
  }

  if (groupCount) {
    if (!supportsGroupCountMode(groupForm.event)) {
      groupMessage.value = '组数分组适用于跳远、跳高、铅球等田赛项目，以及800米及以上长跑项目';
      window.alert(groupMessage.value);
      return;
    }

    const pool = shuffleArray(ungrouped.value);
    const actualGroupCount = Math.min(groupCount, pool.length);
    const baseSize = Math.floor(pool.length / actualGroupCount);
    const remainder = pool.length % actualGroupCount;
    const startIndex = groupedResults.value.length;
    const newGroups = [];
    let cursor = 0;

    for (let idx = 0; idx < actualGroupCount; idx += 1) {
      const chunkSize = baseSize + (idx < remainder ? 1 : 0);
      const picked = pool.slice(cursor, cursor + chunkSize);
      cursor += chunkSize;
      if (!picked.length) continue;
      const label = toChineseGroupNumber(startIndex + newGroups.length + 1);
      const groupRows = buildGroupedRows(picked, label);
      newGroups.push({ event: groupForm.event || '', label, gender: groupForm.gender, rows: groupRows });
    }

    if (!newGroups.length) return;
    groupedResults.value = [...groupedResults.value, ...newGroups];
    groups.value = newGroups[0].rows;
    selectedGroupLabel.value = `${groupForm.event || ''}__${newGroups[0].label}`;
    ungrouped.value = [];
    return;
  }

  const pool = shuffleArray(ungrouped.value);
  const picked = pool.slice(0, perGroup);
  if (!picked.length) return;
  const label = toChineseGroupNumber(groupedResults.value.length + 1);
  const groupRows = buildGroupedRows(picked, label);
  groupedResults.value = [
    ...groupedResults.value,
    { event: groupForm.event || '', label, gender: groupForm.gender, rows: groupRows },
  ];
  groups.value = groupRows;
  selectedGroupLabel.value = `${groupForm.event || ''}__${label}`;
  const pickedKeys = new Set(picked.map((row) => row.id ?? row.student_id));
  ungrouped.value = ungrouped.value.filter((row) => !pickedKeys.has(row.id ?? row.student_id));
};

const confirmGroups = async () => {
  groupMessage.value = '';
  try {
    const allRows = groupedResults.value.length
      ? groupedResults.value.flatMap((item) => item.rows)
      : groups.value;
    if (!allRows.length) {
      groupMessage.value = '暂无可保存的分组结果';
      window.alert(groupMessage.value);
      return;
    }
    const payloadGroups = allRows.map((row) => ({
      event: row.event || groupForm.event,
      college: row.college,
      student_id: row.student_id,
      name: row.name,
      group_label: row.group_label,
      lane: row.lane ?? null,
      round: groupForm.round,
    }));
    await api.post('/groups/confirm', {
      event: groupForm.event,
      round: groupForm.round,
      gender: groupForm.gender,
      groups: payloadGroups,
    });
    groups.value = [];
    selectedGroupLabel.value = '';
    groupMessage.value = '分组保存成功';
    window.alert(groupMessage.value);
  } catch (error) {
    groupMessage.value = error?.response?.data?.detail || '分组保存失败';
    window.alert(groupMessage.value);
  }
};

const buildGroupExportUrl = (path) => {
  const params = new URLSearchParams();
  const event = groupQuery.event || groupForm.event;
  const gender = groupQuery.gender || groupForm.gender;
  const round = groupQuery.round || groupForm.round;
  if (event) params.set('event', event);
  if (gender) params.set('gender', gender);
  if (round) params.set('round', round);
  const query = params.toString();
  return `${api.defaults.baseURL}${path}${query ? `?${query}` : ''}`;
};

const exportGroupsTemplate = () => window.open(buildGroupExportUrl('/export/groups-template'), '_blank');
const exportGroups = () => window.open(buildGroupExportUrl('/export/groups'), '_blank');
const queryGroupCandidates = async () => {
  if (!groupForm.event || !groupForm.gender) {
    groupMessage.value = !groupForm.event ? '请先选择项目' : '请先选择性别';
    window.alert(groupMessage.value);
    return;
  }
  groupMessage.value = '';
  const { data } = await api
    .get('/groups/candidates', {
      params: { event: groupForm.event, gender: groupForm.gender, round: groupForm.round },
    })
    .catch((error) => {
      const detail = error?.response?.data?.detail;
      if (detail) {
        groupMessage.value = detail;
        window.alert(detail);
      }
      return { data: [] };
    });
  ungrouped.value = data || [];
  groups.value = [];
  groupedResults.value = [];
  selectedGroupLabel.value = '';
};

const queryGroups = async () => {
  groupMessage.value = '';
  if (!groupQuery.event || !groupQuery.gender || !groupQuery.round) {
    groupMessage.value = '';
    window.alert(groupMessage.value);
    return;
  }
  const params = {};
  if (groupQuery.event) params.event = groupQuery.event;
  if (groupQuery.gender) params.gender = groupQuery.gender;
  if (groupQuery.round) params.round = groupQuery.round;
  const { data } = await api.get('/groups', { params }).catch(() => ({ data: [] }));
  loadGroupResultsByRows(data || [], false, groupQuery.gender);
};

const selectGroup = (event, label) => {
  const key = `${event || ''}__${label || ''}`;
  selectedGroupLabel.value = key;
  const match = groupedResults.value.find((item) => item.event === event && item.label === label);
  groups.value = match ? match.rows : [];
};

const fetchResults = async () => {
  const params = {};
  if (resultForm.event) params.event = resultForm.event;
  if (resultsQuery.gender) params.gender = resultsQuery.gender;
  if (resultsQuery.round) params.round = resultsQuery.round;
  const { data } = await api.get('/results/list', { params }).catch(() => ({ data: [] }));
  results.value = data || [];
};

const exportResults = () => {
  const params = new URLSearchParams();
  const exportEvent = resultsQuery.event || resultForm.event;
  if (!exportEvent) {
    window.alert('请先选择项目');
    return;
  }
  params.set('event', exportEvent);
  if (resultsQuery.gender) params.set('gender', resultsQuery.gender);
  if (resultsQuery.college) params.set('college', resultsQuery.college);
  if (resultsQuery.name) params.set('name', resultsQuery.name);
  if (resultsQuery.student_id) params.set('student_id', resultsQuery.student_id);
  if (resultsQuery.round) params.set('round', resultsQuery.round);
  const query = params.toString();
  const url = `${api.defaults.baseURL}/export/results${query ? `?${query}` : ''}`;
  window.open(url, '_blank');
};
const exportResultsTemplate = () => {
  const params = new URLSearchParams();
  const exportEvent = resultsQuery.event || resultForm.event;
  if (!exportEvent) {
    window.alert('请先选择项目');
    return;
  }
  params.set('event', exportEvent);
  if (resultsQuery.gender) params.set('gender', resultsQuery.gender);
  if (resultsQuery.round) params.set('round', resultsQuery.round);
  const query = params.toString();
  const url = `${api.defaults.baseURL}/export/results-template${query ? `?${query}` : ''}`;
  window.open(url, '_blank');
};

const initPersonalRanking = async () => {
  await api.post('/rankings/personal/initialize');
  await fetchPersonalRanking();
  await fetchTeamRanking();
};
const initCollegeRanking = async () => {
  await api.post('/rankings/college/initialize');
  await fetchCollegeRanking();
  await fetchTeamRanking();
};

const fetchPersonalRanking = async () => {
  const { data } = await api.get('/rankings/personal/list').catch(() => ({ data: [] }));
  personalRankings.value = data || [];
};

const fetchCollegeRanking = async () => {
  const { data } = await api.get('/rankings/college/list').catch(() => ({ data: [] }));
  collegeRankings.value = data || [];
};

const fetchTeamRanking = async () => {
  const { data } = await api.get('/rankings/team/list').catch(() => ({ data: { male: [], female: [] } }));
  teamRankings.value = {
    male: data?.male || [],
    female: data?.female || [],
  };
};

const exportPersonalRanking = () => window.open(`${api.defaults.baseURL}/export/personal-rankings`, '_blank');
const exportCollegeRanking = () => window.open(`${api.defaults.baseURL}/export/college-rankings`, '_blank');

const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toISOString().slice(0, 10);
};

const searchResults = async () => {
  const params = {};
  if (resultsQuery.event) params.event = resultsQuery.event;
  if (resultsQuery.gender) params.gender = resultsQuery.gender;
  if (resultsQuery.college) params.college = resultsQuery.college;
  if (resultsQuery.name) params.name = resultsQuery.name;
  if (resultsQuery.student_id) params.student_id = resultsQuery.student_id;
  if (resultsQuery.round) params.round = resultsQuery.round;
  const { data } = await api.get('/results/list', { params }).catch(() => ({ data: [] }));
  results.value = data || [];
};

const resultsTable = computed(() => results.value);

const queryRoundGroups = computed(() => {
  const order = ['prelim', 'semi', 'final', 'one'];
  const labels = { prelim: '\u9884\u8d5b', semi: '\u534a\u51b3\u8d5b', final: '\u51b3\u8d5b', one: '\u4e00\u8f6e\u6b21' };
  const bucket = new Map();

  for (const row of resultsTable.value) {
    const key = row?.round || 'unknown';
    if (!bucket.has(key)) {
      bucket.set(key, []);
    }
    bucket.get(key).push(row);
  }

  return Array.from(bucket.entries())
    .sort((a, b) => {
      const ia = order.indexOf(a[0]);
      const ib = order.indexOf(b[0]);
      const oa = ia === -1 ? 99 : ia;
      const ob = ib === -1 ? 99 : ib;
      if (oa !== ob) return oa - ob;
      return String(a[0]).localeCompare(String(b[0]));
    })
    .map(([round, rows]) => ({
      round,
      label: labels[round] || round,
      rows,
    }));
});

const fetchEventOptions = async () => {
  const { data } = await api.get('/events/options').catch(() => ({ data: [] }));
  eventOptions.value = data || [];
};

const queryRoster = async () => {
  if (!resultForm.event || !resultForm.gender) {
    roster.value = [];
    resultMessage.value = !resultForm.event ? '请先选择项目' : '请先选择性别';
    window.alert(resultMessage.value);
    return;
  }
  resultMessage.value = '';

  const fetchGroupRows = async (roundValue) => {
    const params = { event: resultForm.event, gender: resultForm.gender, round: roundValue };
    const resp = await api.get('/groups', { params }).catch(() => ({ data: [] }));
    return resp.data || [];
  };

  const groupRows = await fetchGroupRows(resultForm.round);

  if (!groupRows.length) {
    roster.value = [];
    resultMessage.value = resultForm.round === 'final'
      ? '\u672a\u627e\u5230\u51b3\u8d5b\u5206\u7ec4\u540d\u5355\uff0c\u8bf7\u5148\u5728\u5206\u7ec4\u7ba1\u7406\u4e2d\u5b8c\u6210\u51b3\u8d5b\u5206\u7ec4'
      : '\u672a\u627e\u5230\u53ef\u5f55\u5165\u6210\u7ee9\u7684\u5206\u7ec4\u540d\u5355';
    window.alert(resultMessage.value);
    return;
  }

  const rosterSource = groupRows.map((row) => ({
    id: row.id,
    college: row.college,
    name: row.name,
    student_id: row.student_id,
    event: row.event,
    group_label: normalizeGroupLabel(row.group_label),
    lane: row.lane,
  }));

  const resultsData = await api
    .get('/results/list', { params: { event: resultForm.event, round: resultForm.round } })
    .catch(() => ({ data: [] }));
  const resultMap = new Map(
    (resultsData.data || [])
      .filter((r) => r.event === resultForm.event)
      .map((r) => [r.student_id, r])
  );

  const attemptField = (round, idx) => (
    round === 'prelim' || round === 'semi' ? `prelim_attempt${idx}` : `final_attempt${idx}`
  );

  roster.value = (rosterSource || [])
    .map((row) => {
      const matched = resultMap.get(row.student_id);
      return {
        ...row,
        inputScore: matched?.score ?? row.score ?? '',
        attempt1: matched ? (matched[attemptField(resultForm.round, 1)] ?? '') : '',
        attempt2: matched ? (matched[attemptField(resultForm.round, 2)] ?? '') : '',
        attempt3: matched ? (matched[attemptField(resultForm.round, 3)] ?? '') : '',
        rank: matched?.rank ?? row.rank ?? '',
        date: matched?.date ?? '',
      };
    })
    .sort((rowA, rowB) => {
      const groupCompare = groupLabelOrderValue(rowA?.group_label) - groupLabelOrderValue(rowB?.group_label);
      if (groupCompare !== 0) return groupCompare;
      const laneA = rowA?.lane ?? 999;
      const laneB = rowB?.lane ?? 999;
      if (laneA !== laneB) return laneA - laneB;
      return String(rowA?.name || '').localeCompare(String(rowB?.name || ''));
    });
  resultsQuery.event = resultForm.event;
};


const submitBatchResults = async () => {
  if (!resultForm.event || !resultForm.round) return;
  resultMessage.value = '';
  const timestamp = new Date().toISOString();
  const payload = isDistanceEvent(resultForm.event)
    ? roster.value.flatMap((row) => {
        const attempts = [row.attempt1, row.attempt2, row.attempt3];
        return attempts
          .map((val, idx) => ({ val, idx }))
          .filter((item) => item.val !== '' && item.val !== null && item.val !== undefined)
          .map((item) => ({
            event: resultForm.event,
            student_id: row.student_id,
            round: resultForm.round,
            score: Number(item.val),
            attempt: item.idx + 1,
            date: timestamp,
          }));
      })
    : roster.value
        .filter((row) => row.inputScore !== '' && row.inputScore !== null)
        .map((row) => ({
          event: resultForm.event,
          student_id: row.student_id,
          round: resultForm.round,
          score: Number(row.inputScore),
          date: timestamp,
        }));
  if (!payload.length) {
    resultMessage.value = '';
    return;
  }
  try {
    const submitUrl = isDistanceEvent(resultForm.event) ? '/results-distance/submit' : '/results/submit';
    for (const item of payload) {
      await api.post(submitUrl, item);
    }
    resultMessage.value = '\u4fdd\u5b58\u6210\u529f';
    resultsQuery.event = resultForm.event;
    resultsQuery.round = resultForm.round;
    await searchResults();
    await fetchPersonalRanking();
    await fetchCollegeRanking();
    await fetchTeamRanking();
  } catch (error) {
    const detail = error?.response?.data?.detail;
    resultMessage.value = detail || 'Save failed';
    window.alert(resultMessage.value);
  }
};

onMounted(() => {
  fetchAthletes();
  fetchEventOptions();
  fetchEvents();
  fetchResults();
  fetchPersonalRanking();
  fetchCollegeRanking();
  fetchTeamRanking();
});
</script>


<style scoped>

.distance-score {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.distance-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(90px, 1fr));
  gap: 8px;
}
.score-input {
  display: flex;
  align-items: center;
  gap: 8px;
}
.unit-badge {
  min-width: 48px;
  padding: 6px 10px;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  background: #f6f8fa;
  color: #24292f;
  text-align: center;
  white-space: nowrap;
}


.nav-submenu {
  margin: 6px 0 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.nav-sub-item {
  border: 1px solid #2f3b4d;
  background: #0b1320;
  color: #c7d2e0;
  border-radius: 8px;
  padding: 8px 10px;
  text-align: left;
  cursor: pointer;
}
.nav-sub-item.active {
  background: #162235;
  color: #fff;
}
</style>







