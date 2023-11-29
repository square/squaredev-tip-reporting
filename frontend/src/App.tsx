import { AppShell, Container, Select, MultiSelect, Group, Button, Space, Skeleton } from '@mantine/core';
import { useEffect, useState } from 'react';
import { DateTimePicker } from '@mantine/dates';
import {UsersStack, UsersStackProps } from './components/report-table';
import { useDisclosure } from '@mantine/hooks';
import CustomModal from './components/modal';
import IntroHeading from './components/intro-heading';

interface Report {
  location_id: string;
  team_member_ids: string[];
  start_date: Date;
  end_date: Date;
}

export default function App() {
  const DEFAULT_START_DATE = new Date(Date.now() - 1000 * 60 * 60 * 24 * 7);
  const DEFAULT_END_DATE = new Date(Date.now() + 1000 * 60 * 60 * 24 * 7);
  const [locations, setLocations] = useState([]);
  const [team, setTeam] = useState([]);
  const [report, setReport] = useState<Report>({
    location_id: '',
    team_member_ids: [],
    start_date: DEFAULT_START_DATE,
    end_date: DEFAULT_END_DATE,
  });
  const [reportData, setReportData] = useState<UsersStackProps[]>([]);
  const [showReport, setShowReport] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState({
    selected_team_member_name: "",
    orders: []
  });
  const [opened, { open, close }] = useDisclosure(false);
  const [isModalLoading, setIsModalLoading] = useState(false);

  useEffect(() => {
    fetch('/locations', {
      method: 'GET',
    }).then((response) => {
      response.json().then((data) => {
        const locationData = data.map((location: { id: string; name: string; }) => {
          return { value: location.id, label: location.name };
        });
        setLocations(locationData);
      });
    });
  }, []);

  const getTeam = (event: any) => {
    fetch(`/team?location_id=${event}`, {
      method: 'GET',
    }).then((response) => {
      response.json().then((data) => {
        const teamData = data.map((team_member: { id: string; name: string; }) => {
          return { value: team_member.id, label: team_member.name };
        });
        setReport({ ...report, location_id: event, team_member_ids: teamData.map((x: {label:string, value: string}) => x.value)});
        setTeam(teamData);
      });
    });
  };

  return (
    <AppShell
      padding="md"
      styles={(theme) => ({
        main: { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0] },
      })}
    >
      <Container>
        <IntroHeading/>
        <Select
          label="Select location"
          placeholder="Pick one"
          data={locations}
          onChange={getTeam}
        />
        <MultiSelect
          label="Select team members"
          placeholder="Pick one or more team members"
          data={team}
          value={report.team_member_ids}
          onChange={(event) => setReport({ ...report, team_member_ids: event })}
        />
        <Group spacing="xs">
          <DateTimePicker
            label="Start date"
            placeholder="Pick start date and time"
            valueFormat="DD MMM YYYY hh:mm A"
            defaultValue={DEFAULT_START_DATE}
          />
          <DateTimePicker
            label="End date"
            placeholder="Pick end date and time"
            valueFormat="DD MMM YYYY hh:mm A"
            defaultValue={DEFAULT_END_DATE}
          />
        </Group>
        <Space h="md" />
        <Button variant="filled" color="green" onClick={
          () => {
            setShowReport(true);
            fetch('/tip-report', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                ...report,
                start_date: report.start_date.toISOString(),
                end_date: report.end_date.toISOString()
              })
          }).then((response) => {
            response.json().then((data) => {
              setReportData(Object.values(data));
            });
          });
        }}>
          Run report
        </Button>
      </Container>
      <Container>
        {(showReport) ? 
          (reportData.length > 0) ? 
            <UsersStack open={open} data={reportData} setSelectedDetails={setSelectedDetails} setIsLoading={setIsModalLoading}/> 
            : 
            <Skeleton height={500} /> 
          : ""}
      </Container>
      <CustomModal opened={opened} close={close} selectedDetails={selectedDetails} isLoading={isModalLoading}/>
    </AppShell>
  );
}
